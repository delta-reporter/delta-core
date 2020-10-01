import os
import datetime
import requests
from art import text2art
from dateutil.relativedelta import relativedelta
from logzero import logger
from io import BytesIO
from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)

from data import crud


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/api/v1/initial_setup", methods=["POST"])
def initial_setup():

    crud.Create.initialise_status_tables()

    data = {"message": "Database initialized successfully"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/status", methods=["GET"])
def get_delta_status():
    logger.info("/api/status")

    data = "Delta Reporter up and running"

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/project", methods=["POST"])
def create_project():
    params = request.get_json(force=True)
    logger.info("/projects/%s", params)

    project_check = crud.Read.project_by_name(params.get("name"))

    if not project_check:
        project_id = crud.Create.create_project(
            params.get("name"), params.get("project_status")
        )
        message = "New project added successfully"
        project_event = {
            "event": "delta_project",
            "data": {
                "name": params.get("name"),
                "project_id": project_id,
                "project_status": params.get("project_status"),
            },
        }
        requests.post(app.config.get("WEBSOCKETS_EVENTS_URI"), json=project_event)
    else:
        project_id = project_check.id
        message = "Project recovered successfully"

    data = {"message": message, "id": project_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


# This is just a simple approach for deleting a project, not ready for use yet
@app.route("/api/v1/project/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    logger.info("/delete_project/%s", project_id)

    message = crud.Delete.delete_project(project_id)

    data = {"message": message}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/projects", methods=["GET"])
def get_projects():
    logger.info("/get_projects/")
    projects = crud.Read.projects()

    if projects:
        data = []
        for project in projects:
            data.append(
                {
                    "project_id": project.id,
                    "name": project.name,
                    "data": project.data,
                    "project_status": project.project_status.name,
                }
            )
    else:
        data = {"message": "No projects were found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/project/<int:project_id>", methods=["GET"])
def get_project(project_id):
    logger.info("/project/%i", project_id)

    result = crud.Read.project_by_id(project_id)

    if result:
        data = {
            "project_id": result.id,
            "name": result.name,
            "data": result.data,
            "project_status": result.project_status.name,
        }
    else:
        data = {"message": "No project with the id provided was found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/launch", methods=["POST"])
def create_launch():
    params = request.get_json(force=True)
    logger.info("/launches/%s", params)

    project_check = crud.Read.project_by_name(params.get("project"))

    if not project_check:
        project_id = crud.Create.create_project(params.get("project"))
    else:
        project_id = project_check.id

    launch_id = crud.Create.create_launch(
        params.get("name"), params.get("data"), project_id
    )

    launch_event = {
        "event": "delta_launch",
        "data": {
            "launch_id": launch_id,
            "launch_status": "In Process",
            "name": params.get("name"),
            "project": params.get("project"),
            "project_id": project_id,
        },
    }

    requests.post(app.config.get("WEBSOCKETS_EVENTS_URI"), json=launch_event)

    data = {"message": "New launch added successfully", "id": launch_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/finish_launch", methods=["PUT"])
def finish_launch():
    params = request.get_json(force=True)
    logger.info("/update_launch/%s", params)

    failed_runs = crud.Read.test_runs_failed_by_launch_id(params.get("launch_id"))

    if failed_runs:
        launch = crud.Update.update_launch(params.get("launch_id"), "Failed")
    else:
        launch = crud.Update.update_launch(params.get("launch_id"), "Successful")

    launch_event = {
        "event": "delta_launch",
        "data": {
            "launch_id": launch.id,
            "launch_status": launch.launch_status.name,
            "name": launch.name,
            "project": launch.project.name,
            "project_id": launch.project_id,
        },
    }

    requests.post(app.config.get("WEBSOCKETS_EVENTS_URI"), json=launch_event)

    data = {"message": "Launch updated successfully", "id": launch.id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/launch/<int:launch_id>", methods=["GET"])
def get_launch(launch_id):
    logger.info("/launch/%i", launch_id)

    result = crud.Read.launch_by_id(launch_id)

    if result:
        data = {
            "launch_id": result.id,
            "name": result.name,
            "data": result.data,
            "project": result.project.name,
            "launch_status": result.launch_status.name,
        }
    else:
        data = {"message": "No launch with the id provided was found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/launch/project/<int:project_id>", methods=["GET"])
def get_launches_by_project_id(project_id):
    logger.info("/launches_by_project_id/%i", project_id)

    result = crud.Read.launch_by_project_id(project_id)

    if result:
        launches = []
        index = -1
        launches_index = {}
        for (
            launch,
            test_run,
            total_count,
            failed_count,
            passed_count,
            running_count,
            incomplete_count,
            skipped_count,
        ) in result:
            if launches == [] or launch.id not in list(launches_index.keys()):
                index = index + 1
                launches_index[launch.id] = index
                launches.append(
                    {
                        "launch_id": launch.id,
                        "project_id": launch.project.id,
                        "name": launch.name,
                        "data": launch.data,
                        "project": launch.project.name,
                        "launch_status": launch.launch_status.name,
                        "test_run_stats": [],
                    }
                )
            launches[launches_index[launch.id]]["test_run_stats"].append(
                {
                    "test_run_id": test_run.id,
                    "test_type": test_run.test_type,
                    "tests_total": total_count if total_count else 0,
                    "tests_failed": failed_count if failed_count else 0,
                    "tests_passed": passed_count if passed_count else 0,
                    "tests_running": running_count if running_count else 0,
                    "tests_incomplete": incomplete_count if incomplete_count else 0,
                    "tests_skipped": skipped_count if skipped_count else 0,
                }
            )
        data = launches
    else:
        data = {"message": "No launch with the project id provided was found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_run", methods=["POST"])
def create_test_run():
    params = request.get_json(force=True)
    logger.info("/create_test_run/%s", params)

    test_run_id = crud.Create.create_test_run(
        params.get("data"),
        params.get("start_datetime"),
        params.get("test_type"),
        params.get("launch_id"),
    )

    data = {"message": "New test run added successfully", "id": test_run_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_run", methods=["PUT"])
def update_test_run():
    params = request.get_json(force=True)
    logger.info("/update_test_run/%s", params)

    test_run_id = crud.Update.update_test_run(
        params.get("test_run_id"),
        params.get("end_datetime"),
        params.get("test_run_status"),
        params.get("data"),
    )

    data = {"message": "Test run updated successfully", "id": test_run_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_run/<int:test_run_id>", methods=["GET"])
def get_test_run(test_run_id):
    logger.info("/test_run/%i", test_run_id)

    result = crud.Read.test_run_by_id(test_run_id)

    if result:
        data = {
            "test_run_id": result.id,
            "data": result.data,
            "start_datetime": result.start_datetime,
            "end_datetime": result.end_datetime,
            "duration": diff_dates(result.start_datetime, result.end_datetime),
            "test_type": result.test_type,
            "test_run_status": result.test_run_status.name,
            "launch": result.launch.name,
        }
    else:
        data = {"message": "No test run with the id provided was found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_run/launch/<int:launch_id>", methods=["GET"])
def get_test_runs_by_launch_id(launch_id):
    logger.info("/test_run_by_launch_id/%i", launch_id)

    result = crud.Read.test_run_by_launch_id(launch_id)

    if result:
        test_runs = []
        for (
            test_run,
            total_count,
            failed_count,
            passed_count,
            running_count,
            incomplete_count,
            skipped_count,
        ) in result:
            test_runs.append(
                {
                    "test_run_id": test_run.id,
                    "launch_id": test_run.launch.id,
                    "project_id": test_run.launch.project.id,
                    "data": test_run.data,
                    "start_datetime": test_run.start_datetime,
                    "end_datetime": test_run.end_datetime,
                    "duration": diff_dates(
                        test_run.start_datetime, test_run.end_datetime
                    ),
                    "test_type": test_run.test_type,
                    "test_run_status": test_run.test_run_status.name,
                    "launch_name": test_run.launch.name,
                    "launch_status": test_run.launch.launch_status.name,
                    "tests_total": total_count if total_count else 0,
                    "tests_failed": failed_count if failed_count else 0,
                    "tests_passed": passed_count if passed_count else 0,
                    "tests_running": running_count if running_count else 0,
                    "tests_incomplete": incomplete_count if incomplete_count else 0,
                    "tests_skipped": skipped_count if skipped_count else 0,
                }
            )
        data = test_runs
    else:
        data = {"message": "No launch with the launch id provided was found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_suite", methods=["POST"])
def create_test_suite():
    params = request.get_json(force=True)
    logger.info("/create_test_suite/%s", params)

    project_check = crud.Read.project_by_name(params["project"])

    if not project_check:
        project_id = crud.Create.create_project(params["project"])
    else:
        project_id = project_check.id

    test_suite_check = crud.Read.test_suite_by_name_project_test_type(
        params.get("name"), project_id, params.get("test_type")
    )

    if not test_suite_check:
        test_suite_id = crud.Create.create_test_suite(
            params.get("name"), project_id, None, params.get("test_type")
        )
        message = "New test suite added successfully"
    else:
        test_suite_id = test_suite_check.id
        message = "Test suite is already present"

    data = {"message": message, "test_suite_id": test_suite_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_suite_history", methods=["POST"])
def create_test_suite_history():
    params = request.get_json(force=True)
    logger.info("/create_test_suite_history/%s", params)

    project_check = crud.Read.project_by_name(params["project"])

    if not project_check:
        project_id = crud.Create.create_project(params["project"])
    else:
        project_id = project_check.id

    test_suite_check = crud.Read.test_suite_by_name_project_test_type(
        params.get("name"), project_id, params.get("test_type")
    )

    if not test_suite_check:
        test_suite_id = crud.Create.create_test_suite(
            params.get("name"), project_id, None, params.get("test_type")
        )
    else:
        test_suite_id = test_suite_check.id

    test_suite_history_check = crud.Read.test_suite_history_by_suite_id_test_run(
        params.get("test_run_id"), test_suite_id
    )

    if not test_suite_history_check:
        test_suite_history_id = crud.Create.create_test_suite_history(
            params.get("data"),
            params.get("start_datetime"),
            params.get("test_run_id"),
            test_suite_id,
        )
    else:
        test_suite_history_id = test_suite_history_check.id

    data = {
        "message": "New test suite history added successfully",
        "test_suite_history_id": test_suite_history_id,
        "test_suite_id": test_suite_id,
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_suite_history", methods=["PUT"])
def update_test_suite_history():
    params = request.get_json(force=True)
    logger.info("/update_test_suite_history/%s", params)

    crud.Update.update_test_suite_history(
        params.get("test_suite_history_id"),
        params.get("end_datetime"),
        params.get("data"),
        params.get("test_suite_status"),
    )

    data = {"message": "Test suite history updated successfully"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_suite/<int:test_suite_id>", methods=["GET"])
def get_test_suite(test_suite_id):
    logger.info("/test_suite/%i", test_suite_id)

    result = crud.Read.test_suite_by_id(test_suite_id)

    if result:
        data = {
            "test_suite_id": result.id,
            "name": result.name,
            "data": result.data,
            "test_type": result.test_type,
        }
    else:
        data = {"message": "No test suite with the id provided was found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_history", methods=["POST"])
def create_test_history():
    params = request.get_json(force=True)
    logger.info("/create_test_history/%s", params)

    test_check = crud.Read.test_by_name(params.get("name"))

    if not test_check:
        test_id = crud.Create.create_test(
            params.get("name"), None, params.get("test_suite_id")
        )
    else:
        test_id = test_check.id

    message = "New test history added successfully"
    test_history_check = crud.Read.test_history_by_test_id_and_test_run_id(
        test_id, params.get("test_run_id")
    )
    if not test_history_check:
        test_history_id = crud.Create.create_test_history(
            params.get("start_datetime"),
            test_id,
            params.get("test_run_id"),
            params.get("test_suite_history_id"),
            params.get("parameters"),
            params.get("status"),
        )
    else:
        test_history_id = test_history_check.id
        retries = crud.Update.increase_test_history_retry(test_history_check.id)
        crud.Create.create_test_retry(
            test_history_id=test_history_check.id,
            retry_count=retries,
            start_datetime=test_history_check.start_datetime,
            end_datetime=test_history_check.end_datetime,
            trace=test_history_check.trace,
            message=test_history_check.message,
            error_type=test_history_check.error_type,
            media=test_history_check.media,
        )
        crud.Update.clean_test_history_media(test_history_check.id)

        message = "New test retry added successfully"

    data = {
        "message": message,
        "test_history_id": test_history_id,
        "test_id": test_id,
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_history", methods=["PUT"])
def update_test_history():
    params = request.get_json(force=True)
    logger.info("/update_test_history/%s", params)

    test_updated = crud.Update.update_test_history(
        params.get("test_history_id"),
        params.get("end_datetime"),
        params.get("trace"),
        params.get("file"),
        params.get("message"),
        params.get("error_type"),
        params.get("test_status"),
    )

    # identifying if test is flaky
    latest_runs_by_test_id = crud.Read.test_history_by_test_id(test_updated.test_id)
    if latest_runs_by_test_id:
        flaky_tests = []
        for flaky_test_history in latest_runs_by_test_id:
            if flaky_test_history.test_status.name == "Failed":
                flaky_tests.append({"test_history_id": flaky_test_history.id})
        if len(flaky_tests) > 5:
            crud.Update.update_test_flaky_flag(test_updated.test_id, "true")
        else:
            crud.Update.update_test_flaky_flag(test_updated.test_id, "false")
    else:
        crud.Update.update_test_flaky_flag(test_updated.test_id, "false")

    data = {"message": "Test history updated successfully"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_history_resolution", methods=["PUT"])
def update_test_history_resolution():
    params = request.get_json(force=True)
    logger.info("/update_test_history_resolution/%s", params)

    test_history = crud.Update.update_test_history_resolution(
        params.get("test_history_id"), params.get("test_resolution")
    )

    test = crud.Update.update_general_test_resolution(
        params.get("test_id"), params.get("test_resolution")
    )

    resolution_event = {
        "event": "delta_resolution",
        "data": {
            "test_history_resolution": test_history.test_resolution_id,
            "test_resolution": test.test_resolution_id,
            "test_history_id": test_history.id,
            "test_id": test.id,
        },
    }
    requests.post(app.config.get("WEBSOCKETS_EVENTS_URI"), json=resolution_event)

    data = {
        "message": "Test history resolution updated successfully",
        "resolution": test_history.test_resolution_id,
        "test_history_id": test_history.id,
        "test_id": test.id,
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/tests_suite_history/test_run/<int:test_run_id>", methods=["GET"])
def get_tests_suite_history_by_test_run(test_run_id):
    logger.info("/get_tests_suite_history_by_test_run/%i", test_run_id)

    results = crud.Read.test_suite_history_by_test_run(test_run_id)

    if results:
        test_suites_history = []

        for table in results:
            test_suite_history = table[1]
            test_suites_history.append(
                {
                    "test_suite_history_id": test_suite_history.id,
                    "test_suite_id": test_suite_history.test_suite.id,
                    "name": test_suite_history.test_suite.name,
                    "start_datetime": test_suite_history.start_datetime,
                    "end_datetime": test_suite_history.end_datetime,
                    "duration": diff_dates(
                        test_suite_history.start_datetime,
                        test_suite_history.end_datetime,
                    ),
                    "test_suite_status": test_suite_history.test_suite_status.name,
                }
            )
        data = test_suites_history
    else:
        data = {"message": "No tests suites were found"}
    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route(
    "/api/v1/tests_suite_history/test_status/<int:test_suite_status_id>/test_run/<int:test_run_id>",
    methods=["GET"],
)
def get_tests_suite_history_by_test_status_and_test_run_id(
    test_suite_status_id, test_run_id
):
    logger.info(
        "/tests_suite_history/test_status/%i/test_run/%i/",
        test_suite_status_id,
        test_run_id,
    )

    results = crud.Read.test_suite_history_by_test_status_and_test_run_id(
        test_suite_status_id, test_run_id
    )

    if results:
        test_suites_history = []

        for table in results:
            test_suite_history = table[1]
            test_suites_history.append(
                {
                    "test_suite_history_id": test_suite_history.id,
                    "test_suite_id": test_suite_history.test_suite.id,
                    "name": test_suite_history.test_suite.name,
                    "start_datetime": test_suite_history.start_datetime,
                    "end_datetime": test_suite_history.end_datetime,
                    "duration": diff_dates(
                        test_suite_history.start_datetime,
                        test_suite_history.end_datetime,
                    ),
                    "test_suite_status": test_suite_history.test_suite_status.name,
                }
            )
        data = test_suites_history
    else:
        data = {"message": "No tests suites were found"}
    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/tests_history/test_run/<int:test_run_id>", methods=["GET"])
def get_tests_history_by_test_run(test_run_id):
    logger.info("/get_tests_history_by_test_run/%i", test_run_id)

    results = crud.Read.test_history_by_test_run(test_run_id)

    if results:
        test_suites = []
        test_suites_index = {}
        index = -1

        test_run = {
            "test_run_id": results[0][0].id,
            "launch_id": results[0][0].launch.id,
            "project_id": results[0][0].launch.project.id,
            "project_name": results[0][0].launch.project.name,
            "launch": results[0][0].launch.name,
            "test_type": results[0][0].test_type,
            "start_datetime": results[0][0].start_datetime,
            "end_datetime": results[0][0].end_datetime,
            "duration": diff_dates(
                results[0][0].start_datetime, results[0][0].end_datetime
            ),
            "test_run_status": results[0][0].test_run_status.name,
            "test_run_data": results[0][0].data,
        }
        for table in results:
            test_suite_history = table[1]
            test_history = table[2]
            total_count = table[3]
            failed_count = table[4]
            passed_count = table[5]
            running_count = table[6]
            incomplete_count = table[7]
            skipped_count = table[8]
            if test_suites == [] or test_suite_history.id not in list(
                test_suites_index.keys()
            ):
                index = index + 1
                test_suites_index[test_suite_history.id] = index
                test_suites.append(
                    {
                        "test_suite_history_id": test_suite_history.id,
                        "test_suite_id": test_suite_history.test_suite.id,
                        "name": test_suite_history.test_suite.name,
                        "start_datetime": test_suite_history.start_datetime,
                        "end_datetime": test_suite_history.end_datetime,
                        "duration": diff_dates(
                            test_suite_history.start_datetime,
                            test_suite_history.end_datetime,
                        ),
                        "test_suite_status": test_suite_history.test_suite_status.name,
                        "tests_total": total_count if total_count else 0,
                        "tests_failed": failed_count if failed_count else 0,
                        "tests_passed": passed_count if passed_count else 0,
                        "tests_running": running_count if running_count else 0,
                        "tests_incomplete": incomplete_count if incomplete_count else 0,
                        "tests_skipped": skipped_count if skipped_count else 0,
                        "tests": [],
                    }
                )
            test_suites[test_suites_index.get(test_suite_history.id)]["tests"].append(
                {
                    "test_history_id": test_history.id,
                    "mother_test_id": test_history.mother_test_id,
                    "name": test_history.mother_test.name,
                    "trace": test_history.trace,
                    "file": test_history.file,
                    "message": test_history.message,
                    "error_type": test_history.error_type,
                    "retries": test_history.retries,
                    "start_datetime": test_history.start_datetime,
                    "end_datetime": test_history.end_datetime,
                    "duration": diff_dates(
                        test_history.start_datetime, test_history.end_datetime
                    ),
                    "status": test_history.test_status.name,
                    "test_history_resolution": test_history.test_resolution.id,
                    "test_resolution": test_history.mother_test.test_resolution_id,
                    "parameters": test_history.parameters,
                    "media": test_history.media,
                    "is_flaky": test_history.mother_test.is_flaky,
                }
            )
        test_run["test_suites"] = test_suites
        data = [test_run]
    else:
        data = {"message": "No tests were found"}
    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route(
    "/api/v1/tests_history/test_status/<test_statuses_ids>/test_run/<int:test_run_id>",
    methods=["GET"],
)
def get_tests_history_by_test_status_and_test_run_id(test_statuses_ids, test_run_id):
    logger.info(
        "/tests_history/test_status/%s/test_run/%i/", test_statuses_ids, test_run_id
    )

    tests_history = crud.Read.test_history_by_array_of_test_statuses_and_test_run_id(
        test_statuses_ids=test_statuses_ids, test_run_id=test_run_id
    )

    if tests_history:
        test_suites = []
        test_suites_index = {}
        index = -1

        test_run = {
            "test_run_id": tests_history[0][0].id,
            "launch_id": tests_history[0][0].launch.id,
            "project_id": tests_history[0][0].launch.project.id,
            "launch": tests_history[0][0].launch.name,
            "test_type": tests_history[0][0].test_type,
            "start_datetime": tests_history[0][0].start_datetime,
            "end_datetime": tests_history[0][0].end_datetime,
            "duration": diff_dates(
                tests_history[0][0].start_datetime, tests_history[0][0].end_datetime
            ),
            "test_run_status": tests_history[0][0].test_run_status.name,
            "test_run_data": tests_history[0][0].data,
        }
        for table in tests_history:
            test_suite_history = table[1]
            test_history = table[2]
            total_count = table[3]
            failed_count = table[4]
            passed_count = table[5]
            running_count = table[6]
            incomplete_count = table[7]
            skipped_count = table[8]
            if test_suites == [] or test_suite_history.id not in list(
                test_suites_index.keys()
            ):
                index = index + 1
                test_suites_index[test_suite_history.id] = index
                test_suites.append(
                    {
                        "test_suite_history_id": test_suite_history.id,
                        "test_suite_id": test_suite_history.test_suite.id,
                        "name": test_suite_history.test_suite.name,
                        "start_datetime": test_suite_history.start_datetime,
                        "end_datetime": test_suite_history.end_datetime,
                        "duration": diff_dates(
                            test_suite_history.start_datetime,
                            test_suite_history.end_datetime,
                        ),
                        "test_suite_status": test_suite_history.test_suite_status.name,
                        "tests_total": total_count if total_count else 0,
                        "tests_failed": failed_count if failed_count else 0,
                        "tests_passed": passed_count if passed_count else 0,
                        "tests_running": running_count if running_count else 0,
                        "tests_incomplete": incomplete_count if incomplete_count else 0,
                        "tests_skipped": skipped_count if skipped_count else 0,
                        "tests": [],
                    }
                )
            test_suites[test_suites_index.get(test_suite_history.id)]["tests"].append(
                {
                    "test_history_id": test_history.id,
                    "mother_test_id": test_history.mother_test_id,
                    "name": test_history.mother_test.name,
                    "trace": test_history.trace,
                    "file": test_history.file,
                    "message": test_history.message,
                    "error_type": test_history.error_type,
                    "retries": test_history.retries,
                    "start_datetime": test_history.start_datetime,
                    "end_datetime": test_history.end_datetime,
                    "duration": diff_dates(
                        test_history.start_datetime, test_history.end_datetime
                    ),
                    "status": test_history.test_status.name,
                    "test_history_resolution": test_history.test_resolution.id,
                    "test_resolution": test_history.mother_test.test_resolution_id,
                    "parameters": test_history.parameters,
                    "media": test_history.media,
                }
            )
        test_run["test_suites"] = test_suites
        data = [test_run]
    else:
        data = {"message": "No tests were found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/tests_history/test_status/<int:test_status_id>", methods=["GET"])
def get_tests_history_by_test_status_id(test_status_id):
    logger.info("/tests_history_by_test_status_id/%i", test_status_id)

    tests_history = crud.Read.test_history_by_test_status_id(test_status_id)

    if tests_history:
        data = []
        for test_history in tests_history:
            data.append(
                {
                    "test_history_id": test_history.id,
                    "name": test_history.mother_test.name,
                    "start_datetime": test_history.start_datetime,
                    "end_datetime": test_history.end_datetime,
                    "duration": diff_dates(
                        test_history.start_datetime, test_history.end_datetime
                    ),
                    "test_status": test_history.test_status.name,
                    "test_resolution": test_history.test_resolution.name,
                    "test_media": test_history.media,
                }
            )
    else:
        data = {"message": "No tests were found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route(
    "/api/v1/tests_history/test_resolution/<int:test_resolution_id>", methods=["GET"]
)
def get_tests_history_by_test_resolution_id(test_resolution_id):
    logger.info("/tests_history_by_test_resolution_id/%i", test_resolution_id)

    tests_history = crud.Read.test_history_by_test_resolution_id(test_resolution_id)

    if tests_history:
        data = []
        for test_history in tests_history:
            data.append(
                {
                    "test_history_id": test_history.id,
                    "name": test_history.mother_test.name,
                    "start_datetime": test_history.start_datetime,
                    "end_datetime": test_history.end_datetime,
                    "duration": diff_dates(
                        test_history.start_datetime, test_history.end_datetime
                    ),
                    "test_status": test_history.test_status.name,
                    "test_resolution": test_history.test_resolution.name,
                    "test_media": test_history.media,
                }
            )
    else:
        data = {"message": "No tests were found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/tests_history/test_suite/<int:test_suite_id>", methods=["GET"])
def get_tests_history_by_test_suite_id(test_suite_id):
    logger.info("/tests_history_by_test_suite_id/%i", test_suite_id)

    results = crud.Read.test_history_by_test_suite_id(test_suite_id)

    if results:
        data = []
        for table in results:
            test_history = table[0]
            test = table[1]
            test_suite = table[2]
            data.append(
                {
                    "test_history_id": test_history.id,
                    "name": test.name,
                    "start_datetime": test_history.start_datetime,
                    "end_datetime": test_history.end_datetime,
                    "duration": diff_dates(
                        test_history.start_datetime, test_history.end_datetime
                    ),
                    "test_status": test_history.test_status.name,
                    "test_resolution": test_history.test_resolution.name,
                    "test_suite": test_suite.name,
                    "test_type": test_suite.name,
                    "test_media": test_history.media,
                }
            )
    else:
        data = {"message": "No tests were found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/tests_retries/<int:test_history_id>", methods=["GET"])
def get_test_retries_by_test_history_id(test_history_id):
    logger.info("/test_retries_by_test_history_id/%i", test_history_id)

    results = crud.Read.test_retries_by_test_history_id(test_history_id)

    if results:
        data = []
        for test_retry in results:
            data.append(
                {
                    "id": test_retry.id,
                    "test_history_id": test_retry.test_history_id,
                    "start_datetime": test_retry.start_datetime,
                    "end_datetime": test_retry.end_datetime,
                    "duration": diff_dates(
                        test_retry.start_datetime, test_retry.end_datetime
                    ),
                    "retry_count": test_retry.retry_count,
                    "trace": test_retry.trace,
                    "message": test_retry.message,
                    "error_type": test_retry.error_type,
                    "media": test_retry.media,
                }
            )
    else:
        data = {"message": "No test retries were found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/file_receiver_test_history/<int:test_history_id>", methods=["POST"])
def receive_file_for_test_history(test_history_id):
    logger.info("/receive_file_for_test_history/%i", test_history_id)

    file = request.files.get("file")
    type = request.form.get("type")
    description = request.form.get("description", "")
    file_id = crud.Create.store_media_file(file.filename, type, file.read())

    crud.Update.add_media_to_test_history(
        test_history_id,
        {
            "file_id": file_id,
            "filename": file.filename,
            "type": type,
            "description": description,
        },
    )

    data = {"message": "File stored successfully", "file_id": file_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_history/test_id/<int:test_id>", methods=["GET"])
def get_test_history_by_test_id(test_id):
    logger.info("/tests_history_by_test_id/%i", test_id)
    status = 200

    results = crud.Read.test_history_by_test_id(test_id)

    if results:
        data = []
        for test_history in results:
            data.append(
                {
                    "test_history_id": test_history.id,
                    "start_datetime": test_history.start_datetime,
                    "end_datetime": test_history.end_datetime,
                    "duration": diff_dates(
                        test_history.start_datetime, test_history.end_datetime
                    ),
                    "status": test_history.test_status.name,
                    "resolution": test_history.test_resolution.id,
                    "trace": test_history.trace,
                    "message": test_history.message,
                    "error_type": test_history.error_type,
                    "media": test_history.media,
                }
            )
    else:
        data = {"message": "No history was found"}
        status = 204

    resp = jsonify(data)
    resp.status_code = status

    return resp


@app.route("/api/v1/get_file/<int:media_id>", methods=["GET"])
def get_file_by_media_id(media_id):
    logger.info("/get_file_by_media_id/%i", media_id)

    file = crud.Read.file_by_media_id(media_id)

    return send_file(BytesIO(file.data), attachment_filename=file.name)


@app.route("/api/v1/update_project_name", methods=["PUT"])
def update_project_name():
    params = request.get_json(force=True)
    logger.info("/update_project_name/%s", params)

    project_name = crud.Update.update_project_name(params.get("id"), params.get("name"))

    data = {
        "message": "Project name updated successfully",
        "project_name": project_name,
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.errorhandler(404)
def notfound(error):
    data = {"message": "The endpoint requested was not found"}

    resp = jsonify(data)
    resp.status_code = 404

    return resp


def diff_dates(date1, date2):
    if not date1:
        return None
    if not date2:
        date2 = datetime.datetime.now()

    diff = relativedelta(date2, date1)

    return {
        "years": diff.years,
        "months": diff.months,
        "days": diff.days,
        "hours": diff.hours,
        "minutes": diff.minutes,
        "seconds": diff.seconds,
        "microseconds": diff.microseconds,
    }


if __name__ == "__main__":
    print("Δ Delta Reporter - Core Service")
    print(
        text2art(
            """Δ Delta Reporter
    Core Service""",
            font="Greek",
        )
    )
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=os.getenv("PORT", 5000))
