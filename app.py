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
from components.smart_links import SmartLinks


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)

from data import crud
import tasks


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
    else:
        project_id = project_check.id
        message = "Project recovered successfully"

    data = {"message": message, "id": project_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/project/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    logger.info("/delete_project/%s", project_id)

    job = tasks.delete_project.delay(project_id)

    data = {"message": "Deletion process started", "job_id": job.id}

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
        project_id = crud.Create.create_project(params.get("project"), "Active")
    else:
        project_id = project_check.id

    launch_id = crud.Create.create_launch(
        params.get("name"), params.get("data"), project_id
    )

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
                    "environment": test_run.environment,
                    "tests_total": none_checker(total_count),
                    "tests_failed": none_checker(failed_count),
                    "tests_passed": none_checker(passed_count),
                    "tests_running": none_checker(running_count),
                    "tests_incomplete": none_checker(incomplete_count),
                    "tests_skipped": none_checker(skipped_count),
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
        params.get("environment"),
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
    )

    data = {"message": "Test run updated successfully", "id": test_run_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_run_data/<int:test_run_id>", methods=["PUT"])
def update_test_run_data(test_run_id):
    params = request.get_json(force=True)
    logger.info("/update_test_run_data/%s", params)

    test_run_id = crud.Update.update_test_run_data(test_run_id, params.get("data"),)

    data = {"message": "Test run data updated successfully", "id": test_run_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_run/<int:test_run_id>", methods=["GET"])
def get_test_run(test_run_id):
    logger.info("/test_run/%i", test_run_id)

    result = crud.Read.test_run_by_id(test_run_id)

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
                    "project_name": test_run.launch.project.name,
                    "data": test_run.data,
                    "start_datetime": test_run.start_datetime,
                    "end_datetime": test_run.end_datetime,
                    "duration": diff_dates(
                        test_run.start_datetime,
                        test_run.end_datetime,
                        test_run.launch.launch_status.name,
                    ),
                    "test_type": test_run.test_type,
                    "environment": test_run.environment,
                    "test_run_status": test_run.test_run_status.name,
                    "launch_name": test_run.launch.name,
                    "launch_status": test_run.launch.launch_status.name,
                    "tests_total": none_checker(total_count),
                    "tests_failed": none_checker(failed_count),
                    "tests_passed": none_checker(passed_count),
                    "tests_running": none_checker(running_count),
                    "tests_incomplete": none_checker(incomplete_count),
                    "tests_skipped": none_checker(skipped_count),
                }
            )
        data = test_runs
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
                        test_run.start_datetime,
                        test_run.end_datetime,
                        test_run.launch.launch_status.name,
                    ),
                    "test_type": test_run.test_type,
                    "environment": test_run.environment,
                    "test_run_status": test_run.test_run_status.name,
                    "launch_name": test_run.launch.name,
                    "launch_status": test_run.launch.launch_status.name,
                    "tests_total": none_checker(total_count),
                    "tests_failed": none_checker(failed_count),
                    "tests_passed": none_checker(passed_count),
                    "tests_running": none_checker(running_count),
                    "tests_incomplete": none_checker(incomplete_count),
                    "tests_skipped": none_checker(skipped_count),
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
        project_id = crud.Create.create_project(params["project"], "Active")
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
        project_id = crud.Create.create_project(params["project"], "Active")
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

    test_check = crud.Read.mother_test_by_name(params.get("name"))

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
    latest_runs_by_test_id = crud.Read.test_history_by_test_id(
        test_updated.mother_test_id
    )
    if latest_runs_by_test_id:
        flaky_tests = []
        for flaky_test_history in latest_runs_by_test_id:
            if flaky_test_history.test_status.name == "Failed":
                flaky_tests.append({"test_history_id": flaky_test_history.id})
        if len(flaky_tests) > 5:
            crud.Update.update_test_flaky_flag(test_updated.mother_test_id, True)
        else:
            crud.Update.update_test_flaky_flag(test_updated.mother_test_id, False)
    else:
        crud.Update.update_test_flaky_flag(test_updated.mother_test_id, False)

    data = {"message": "Test history updated successfully"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_data/<int:test_id>", methods=["PUT"])
def update_test_data(test_id):
    params = request.get_json(force=True)
    logger.info("/update_test_data/%s", params)

    test_id = crud.Update.update_test_data(test_id, params.get("data"),)

    data = {"message": "Test data updated successfully", "id": test_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/test_history_resolution", methods=["PUT"])
def update_test_history_resolution():
    params = request.get_json(force=True)
    logger.info("/update_test_history_resolution/%s", params)

    test = crud.Update.update_test_history_resolution(
        params.get("test_id"), params.get("test_resolution")
    )

    mother_test = crud.Update.update_general_test_resolution(
        params.get("mother_test_id"), params.get("test_resolution")
    )

    data = {
        "message": "Test history resolution updated successfully",
        "resolution": test.test_resolution_id,
        "test_id": test.id,
        "mother_test_id": mother_test.id,
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
                        test_suite_history.test_suite_status.name,
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
                        test_suite_history.test_suite_status.name,
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
    "/api/v1/tests_suites_history/test_status/<test_statuses_ids>/test_run/<int:test_run_id>",
    methods=["GET"],
)
def get_tests_suites_history_by_test_status_and_test_run_id(
    test_statuses_ids, test_run_id
):
    logger.info(
        "/tests_history/test_status/%s/test_run/%i/", test_statuses_ids, test_run_id
    )

    tests_history = crud.Read.test_suite_history_by_array_of_test_statuses_and_test_run_id(
        test_statuses_ids=test_statuses_ids, test_run_id=test_run_id
    )

    if tests_history:
        test_suites = []

        for (
            test_suite_history,
            total_count,
            failed_count,
            passed_count,
            running_count,
            incomplete_count,
            skipped_count,
        ) in tests_history:
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
                        test_suite_history.test_suite_status.name,
                    ),
                    "test_suite_status": test_suite_history.test_suite_status.name,
                    "tests_total": none_checker(total_count),
                    "tests_failed": none_checker(failed_count),
                    "tests_passed": none_checker(passed_count),
                    "tests_running": none_checker(running_count),
                    "tests_incomplete": none_checker(incomplete_count),
                    "tests_skipped": none_checker(skipped_count),
                }
            )
        data = test_suites
    else:
        data = None

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route(
    "/api/v1/tests/test_status/<test_statuses_ids>/test_suite_history/<int:test_suite_history_id>",
    methods=["GET"],
)
def get_tests_history_by_test_status_and_test_suite_history_id(
    test_statuses_ids, test_suite_history_id
):
    logger.info(
        "/tests_history/test_status/%s/test_run/%i/",
        test_statuses_ids,
        test_suite_history_id,
    )

    tests_history = crud.Read.tests_by_array_of_test_statuses_and_test_suite_history_id(
        test_statuses_ids=test_statuses_ids, test_suite_history_id=test_suite_history_id
    )

    if tests_history:
        tests = []
        for test in tests_history:
            tests.append(
                {
                    "test_id": test.id,
                    "mother_test_id": test.mother_test_id,
                    "name": test.mother_test.name,
                    "trace": test.trace,
                    "file": test.file,
                    "message": test.message,
                    "error_type": test.error_type,
                    "retries": test.retries,
                    "start_datetime": test.start_datetime,
                    "end_datetime": test.end_datetime,
                    "duration": diff_dates(
                        test.start_datetime, test.end_datetime, test.test_status.name
                    ),
                    "status": test.test_status.name,
                    "test_history_resolution": test.test_resolution.id,
                    "test_resolution": test.mother_test.test_resolution_id,
                    "parameters": test.parameters,
                    "media": test.media,
                    "is_flaky": test.mother_test.is_flaky,
                }
            )
        data = tests
    else:
        data = None

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
                        test_history.start_datetime,
                        test_history.end_datetime,
                        test_history.test_status.name,
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
                        test_history.start_datetime,
                        test_history.end_datetime,
                        test_history.test_status.name,
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
                        test_retry.start_datetime, test_retry.end_datetime, "Failed"
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
    file_type = request.form.get("type")
    description = request.form.get("description", "")
    file_id = crud.Create.store_media_file(file.filename, file_type, file.read())

    crud.Update.add_media_to_test_history(
        test_history_id,
        {
            "file_id": file_id,
            "filename": file.filename,
            "type": file_type,
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
                        test_history.start_datetime,
                        test_history.end_datetime,
                        test_history.test_status.name,
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


@app.route("/api/v1/notes", methods=["POST"])
def create_note():
    params = request.get_json(force=True)
    logger.info("/notes/%s", params)

    note_id = crud.Create.create_note(
        params.get("mother_test_id"), params.get("note_text"), params.get("added_by")
    )
    message = "New note added successfully"

    data = {"message": message, "id": note_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/notes/<int:mother_test_id>", methods=["GET"])
def get_notes(mother_test_id):
    logger.info("/get_notes/")
    notes = crud.Read.notes_by_mother_test_id(mother_test_id)

    if notes:
        data = []
        for note in notes:
            data.append(
                {
                    "mother_test_id": note.mother_test_id,
                    "note_text": note.note_text,
                    "added_by": note.added_by,
                    "created_datetime": note.created_datetime,
                }
            )
    else:
        data = {"message": "No notes were found"}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/smart_link", methods=["POST"])
def create_smart_link():
    params = request.get_json(force=True)
    logger.info("/create_smart_link/%s", params)

    smart_link_id = crud.Create.create_smart_link(
        params.get("project_id"),
        params.get("environment"),
        params.get("smart_link"),
        params.get("label"),
        params.get("color"),
        params.get("filtered"),
        params.get("location"),
        params.get("datetime_format"),
    )

    message = "New smart link added successfully"

    data = {"message": message, "id": smart_link_id}

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/update_smart_link", methods=["PUT"])
def update_smart_link():
    params = request.get_json(force=True)
    logger.info("/update_smart_link/%s", params)

    crud.Update.update_smart_link(
        params.get("smart_link_id"),
        params.get("environment"),
        params.get("smart_link"),
        params.get("label"),
        params.get("color"),
        params.get("filtered"),
        params.get("location"),
        params.get("datetime_format"),
    )

    data = {
        "message": "SmartLink updated successfully",
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/smart_links/<int:project_id>", methods=["GET"])
def get_smart_links(project_id):
    logger.info("/get_smart_links/")
    smart_links = crud.Read.smart_links_by_project_id(project_id)

    if smart_links:
        data = []
        for sl in smart_links:
            data.append(
                {
                    "smart_link_id": sl.id,
                    "project_id": sl.project_id,
                    "environment": sl.environment,
                    "smart_link": sl.smart_link,
                    "label": sl.label,
                    "color": sl.color,
                    "filtered": sl.filtered,
                    "location": sl.location.name,
                    "datetime_format": sl.datetime_format,
                }
            )
    else:
        data = None

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/smart_links_for_test", methods=["POST"])
def get_smart_links_for_test():
    logger.info("/get_smart_links_for_test/")
    params = request.get_json(force=True)
    test_sl_location_id = 1
    smart_links = crud.Read.smart_links_by_project_id_and_location(
        params.get("project_id"), test_sl_location_id
    )
    test = crud.Read.test_by_id(params.get("test_id"))
    test_data = test.pop("data", None)

    environment = params.get("environment")

    sl_data = []

    if smart_links:
        for sl in smart_links:
            sl_data.append(
                {
                    "smart_link_id": sl.id,
                    "project_id": sl.project_id,
                    "environment": sl.environment,
                    "smart_link": sl.smart_link,
                    "label": sl.label,
                    "color": sl.color,
                    "filtered": sl.filtered,
                    "location": sl.location.name,
                    "datetime_format": sl.datetime_format,
                }
            )
    else:
        data = None

    sl = SmartLinks()

    data = sl.get_smart_links_for_test(sl_data, environment, test, test_data)

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/smart_links_for_test_run", methods=["POST"])
def get_smart_links_for_test_run():
    logger.info("/get_smart_links_for_test_run/")
    params = request.get_json(force=True)
    test_run_sl_location_id = 2
    smart_links = crud.Read.smart_links_by_project_id_and_location(
        params.get("project_id"), test_run_sl_location_id
    )
    test_run = crud.Read.simple_test_run_by_id(params.get("test_run_id"))
    test_run_data = test_run.pop("data", None)

    environment = params.get("environment")

    sl_data = []

    if smart_links:
        for sl in smart_links:
            sl_data.append(
                {
                    "smart_link_id": sl.id,
                    "project_id": sl.project_id,
                    "environment": sl.environment,
                    "smart_link": sl.smart_link,
                    "label": sl.label,
                    "color": sl.color,
                    "filtered": sl.filtered,
                    "location": sl.location.name,
                    "datetime_format": sl.datetime_format,
                }
            )
    else:
        data = None

    sl = SmartLinks()

    data = sl.get_smart_links_for_test_run(
        sl_data, environment, test_run, test_run_data
    )

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/api/v1/delete_smart_link/<int:smart_link_id>", methods=["DELETE"])
def delete_smart_link(smart_link_id):
    logger.info("/delete_smart_link/%s", smart_link_id)

    message = crud.Delete.delete_smart_link(smart_link_id)

    data = {
        "message": message,
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


def diff_dates(date1, date2, status):
    if not date1 or status == "Skipped":
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

@app.route("/api/v1/weekly_stats/<int:project_id>", methods=["GET"])
def get_weekly_stats(project_id):
    logger.info("/weekly_stats/%s", project_id)
    result = crud.Read.week_stats_daily(project_id)

    if result:
        weekly_stats = []
        index = -1
        days_index = {}
        for (
            day,
            total_count,
            failed_count,
            passed_count,
            running_count,
            incomplete_count,
            skipped_count,
        ) in result:
            if weekly_stats == [] or day not in list(days_index.keys()):
                index = index + 1
                days_index[day] = index
                weekly_stats.append(
                    {
                        "date": day,
                        "tests_total": none_checker(total_count),
                        "tests_failed": none_checker(failed_count),
                        "tests_passed": none_checker(passed_count),
                        "tests_running": none_checker(running_count),
                        "tests_incomplete": none_checker(incomplete_count),
                        "tests_skipped": none_checker(skipped_count),
                    }
                )
            weekly_stats[days_index[day]] = {
                    "date": day,
                    "tests_total": none_checker(total_count) + weekly_stats[days_index[day]].get("tests_total"),
                    "tests_failed": none_checker(failed_count) + weekly_stats[days_index[day]].get("tests_failed"),
                    "tests_passed": none_checker(passed_count) + weekly_stats[days_index[day]].get("tests_passed"),
                    "tests_running": none_checker(running_count) + weekly_stats[days_index[day]].get("tests_running"),
                    "tests_incomplete": none_checker(incomplete_count) + weekly_stats[days_index[day]].get("tests_incomplete"),
                    "tests_skipped": none_checker(skipped_count) + weekly_stats[days_index[day]].get("tests_skipped"),
                }
        data = weekly_stats
    else:
        data = None

    resp = jsonify(data)
    resp.status_code = 200

    return resp


def none_checker(element):
    return element if element else 0


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
