import os
from logzero import logger
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import models
from data import crud

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/initial_setup", methods=['POST'])
def initial_setup():
    db.session.add(models.ProjectStatus(name='Active'))
    db.session.add(models.ProjectStatus(name='Inactive'))
    db.session.add(models.ProjectStatus(name='Archived'))
    db.session.add(models.LaunchStatus(name='Failed'))
    db.session.add(models.LaunchStatus(name='In Process'))
    db.session.add(models.LaunchStatus(name='Successful'))
    db.session.add(models.TestSuiteStatus(name='Failed'))
    db.session.add(models.TestSuiteStatus(name='Successful'))
    db.session.add(models.TestSuiteStatus(name='Running'))
    db.session.add(models.TestRunStatus(name='Failed'))
    db.session.add(models.TestRunStatus(name='Passed'))
    db.session.add(models.TestRunStatus(name='Running'))
    db.session.add(models.TestStatus(name='Failed'))
    db.session.add(models.TestStatus(name='Passed'))
    db.session.add(models.TestStatus(name='Running'))
    db.session.add(models.TestStatus(name='Incomplete'))
    db.session.add(models.TestStatus(name='Skipped'))
    db.session.add(models.TestResolution(name='Not set'))
    db.session.add(models.TestResolution(name='Working as expected'))
    db.session.add(models.TestResolution(name='Test Issue'))
    db.session.add(models.TestResolution(name='Environment Issue'))
    db.session.add(models.TestResolution(name='Application Issue'))

    db.session.commit()

    data = {
        'message' : 'Database initialized successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/project", methods=['POST'])
def create_project():
    params = request.get_json(force=True)
    logger.info("/projects/%s", params)

    project_check = models.Project.query.filter_by(name=params['name']).first()

    if not project_check:
        project_id = crud.Create.create_project(params['name'])
        message = 'New project added successfully'
    else:
        project_id = project_check.id
        message = 'Project recovered successfully'

    data = {
        'message' : message,
        'id': project_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_projects", methods=['GET'])
def get_projects():
    logger.info("/get_projects/")
    projects = models.Project.query.all()

    if projects:
        data = []
        for project in projects:
            data.append( {
                'id' : project.id,
                'name' : project.name,
                'data' : project.data,
                'project_status' : project.project_status.name
            })
    else:
        data = {
            'message': 'No projects were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/project/<int:project_id>", methods=['GET'])
def get_project(project_id):
    logger.info("/project/%i", project_id)

    result = models.Project.query.filter_by(id=project_id).first()

    if result:
        data = {
            'id' : result.id,
            'name' : result.name,
            'data' : result.data,
            'project_status' : result.project_status.name
        }
    else:
        data = {
            'message': 'No project with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/launch", methods=['POST'])
def create_launch():
    params = request.get_json(force=True)
    logger.info("/launches/%s", params)

    project_check = models.Project.query.filter_by(name=params['project']).first()

    if not project_check:
        project_id = crud.Create.create_project(params['project'])
    else:
        project_id = project_check.id

    launch_id = crud.Create.create_launch(params['name'], params.get('data'), project_id)

    data = {
        'message' : 'New launch added successfully',
        'id': launch_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_launches", methods=['GET'])
def get_launches():
    logger.info("/get_launches/")
    launches = models.Launch.query.all()

    if launches:
        data = []
        for launch in launches:
            data.append( {
                'id' : launch.id,
                'name' : launch.name,
                'data' : launch.data,
                'project' : launch.project.name,
                'launch_status' : launch.launch_status.name
            })
    else:
        data = {
            'message': 'No launches were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/launch/<int:launch_id>", methods=['GET'])
def get_launch(launch_id):
    logger.info("/launch/%i", launch_id)

    result = models.Launch.query.filter_by(id=launch_id).first()

    if result:
        data = {
            'id'  : result.id,
            'name' : result.name,
            'data' : result.data,
            'project' : result.project.name,
            'launch_status' : result.launch_status.name
        }
    else:
        data = {
            'message' : 'No launch with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_run", methods=['POST'])
def create_test_run():
    params = request.get_json(force=True)
    logger.info("/create_test_run/%s", params)

    test_run_id = crud.Create.create_test_run(params.get('data'), params.get('start_datetime'), params.get('test_type'), params.get('launch_id'))

    data = {
        'message' : 'New test run added successfully',
        'id': test_run_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_run", methods=['PUT'])
def update_test_run():
    params = request.get_json(force=True)
    logger.info("/update_test_run/%s", params)

    test_run_id = crud.Update.update_test_run(params.get('test_run_id'), params.get('end_datetime'), params.get('data'), params.get('test_run_status'))

    data = {
        'message' : 'Test run updated successfully',
        'id': test_run_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_test_runs", methods=['GET'])
def get_test_runs():
    logger.info("/get_test_runs/")
    test_runs = models.TestRun.query.all()

    if test_runs:
        data = []
        for test_run in test_runs:
            data.append( {
                'id'  : test_run.id,
                'data': test_run.data,
                'start_datetime' : test_run.start_datetime,
                'end_datetime' : test_run.end_datetime,
                'test_type' : test_run.test_type,
                'test_run_status' : test_run.test_run_status.name,
                'launch' : test_run.launch.name
            })
    else:
        data = {
            'message': 'No test runs were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_run/<int:test_run_id>", methods=['GET'])
def get_test_run(test_run_id):
    logger.info("/test_run/%i", test_run_id)

    result = models.TestRun.query.filter_by(id=test_run_id).first()

    if result:
        data = {
            'id'  : result.id,
            'data': result.data,
            'start_datetime' : result.start_datetime,
            'end_datetime' : result.end_datetime,
            'test_type' : result.test_type,
            'test_run_status' : result.test_run_status.name,
            'launch' : result.launch.name
        }
    else:
        data = {
            'message' : 'No test run with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_suite", methods=['POST'])
def create_test_suite():
    params = request.get_json(force=True)
    logger.info("/create_test_suite/%s", params)

    test_suite_check = models.TestSuite.query.filter_by(name=params.get('name'), test_type=params.get('test_type')).first()

    if not test_suite_check:
        test_suite_id = crud.Create.create_test_suite(params.get('name'), None, params.get('test_type'))
        message = 'New test suite added successfully'
    else:
        test_suite_id = test_suite_check.id
        message = 'Test suite is already present'

    data = {
        'message' : message,
        'test_suite_id': test_suite_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_suite_history", methods=['POST'])
def create_test_suite_history():
    params = request.get_json(force=True)
    logger.info("/create_test_suite_history/%s", params)

    test_suite_check = models.TestSuite.query.filter_by(name=params.get('name'), test_type=params.get('test_type')).first()

    if not test_suite_check:
        test_suite_id = crud.Create.create_test_suite(params.get('name'), None, params.get('test_type'))
    else:
        test_suite_id = test_suite_check.id

    test_suite_history_id = crud.Create.create_test_suite_history(params.get('data'), params.get('start_datetime'), params.get('test_run_id'), test_suite_id)

    data = {
        'message' : 'New test suite history added successfully',
        'test_suite_history_id': test_suite_history_id,
        'test_suite_id': test_suite_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_suite_history", methods=['PUT'])
def update_test_suite_history():
    params = request.get_json(force=True)
    logger.info("/update_test_suite_history/%s", params)

    crud.Update.update_test_suite_history(params.get('test_suite_history_id'), params.get('end_datetime'), params.get('data'), params.get('test_suite_status'))

    data = {
        'message' : 'Test suite history updated successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_test_suites", methods=['GET'])
def get_test_suites():
    logger.info("/get_test_suites/")
    test_suites = models.TestSuite.query.all()

    if test_suites:
        data = []
        for test_suite in test_suites:
            data.append( {
                'id'  : test_suite.id,
                'name'  : test_suite.name,
                'data': test_suite.data,
                'test_type': test_suite.test_type
            })
    else:
        data = {
            'message': 'No test suites were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_suite/<int:test_suite_id>", methods=['GET'])
def get_test_suite(test_suite_id):
    logger.info("/test_suite/%i", test_suite_id)

    result = models.TestSuite.query.filter_by(id=test_suite_id).first()

    if result:
        data = {
            'id'  : result.id,
            'name'  : result.name,
            'data': result.data,
            'test_type': result.test_type
        }
    else:
        data = {
            'message' : 'No test suite with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test", methods=['POST'])
def create_test():
    params = request.get_json(force=True)
    logger.info("/create_test/%s", params)

    test_check = models.Test.query.filter_by(name=params.get('name')).first()

    if not test_check:
        test_id = crud.Create.create_test(params.get('name'), None, params.get('test_suite_id'))
        message = 'New test added successfully'
    else:
        test_id = test_check.id
        message = 'Test is already present'

    data = {
        'message' : message,
        'test_id': test_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_history", methods=['POST'])
def create_test_history():
    params = request.get_json(force=True)
    logger.info("/create_test_history/%s", params)

    test_check = models.Test.query.filter_by(name=params.get('name')).first()

    if not test_check:
        test_id = crud.Create.create_test(params.get('name'), None, params.get('test_suite_id'))
    else:
        test_id = test_check.id

    test_history_id = crud.Create.create_test_history(params.get('start_datetime'), params.get('data'), test_id, params.get('test_run_id'))

    data = {
        'message' : 'New test history added successfully',
        'test_history_id': test_history_id,
        'test_id': test_id
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_history", methods=['PUT'])
def update_test_history():
    params = request.get_json(force=True)
    logger.info("/update_test_history/%s", params)

    crud.Update.update_test_history(params.get('test_history_id'), params.get('end_datetime'), params.get('data'), params.get('test_status'))

    data = {
        'message' : 'Test history updated successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_tests", methods=['GET'])
def get_tests():
    logger.info("/get_tests/")
    tests = models.Test.query.all()

    if tests:
        data = []
        for test in tests:
            data.append( {
                'id'  : test.id,
                'name' : test.name,
                'data': test.data,
                'test_suite_id': test.test_suite_id
            })
    else:
        data = {
            'message': 'No tests were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/tests_history/test_run_id/<int:test_run_id>", methods=['GET'])
def get_tests_history_by_test_run(test_run_id):
    logger.info("/get_tests_history_by_test_run/%i", test_run_id)

    results = db.session.query(models.TestRun, models.TestSuiteHistory, models.TestHistory)\
        .filter(models.TestRun.id == models.TestSuiteHistory.test_run_id)\
            .filter(models.TestSuiteHistory.test_run_id == models.TestHistory.test_run_id)\
                .filter(models.TestRun.id == test_run_id).all()

    if results:
        data = []
        for table in results:
            test_run = table[0]
            test_suite_history = table[1]
            test_history = table[2]
            data.append( {
                'id'  : test_run.id,
                'launch' : test_run.launch.name,
                'test_type': test_run.test_type,
                'start_datetime': test_run.start_datetime,
                'end_datetime': test_run.end_datetime,
                'test_run_status': test_run.test_run_status.name,
                'test_suite': {
                    'name': test_suite_history.test_suite.name,
                    'start_datetime': test_suite_history.start_datetime,
                    'end_datetime': test_suite_history.end_datetime,
                    'test_suite_status': test_suite_history.test_suite_status.name
                },
                'test': {
                    'name': test_history.test.name,
                    'data': test_history.data,
                    'start_datetime': test_history.start_datetime,
                    'end_datetime': test_history.end_datetime,
                    'status': test_history.test_status.name,
                    'resolution': test_history.test_resolution.name
                }
            })
    else:
        data = {
            'message': 'No tests were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test/<int:test_id>", methods=['GET'])
def get_test_by_test_id(test_id):
    logger.info("/test/%i", test_id)

    result = models.Test.query.filter_by(id=test_id).first()

    if result:
        data = {
            'id'  : result.id,
            'name' : result.name,
            'data': result.data,
            'test_suite_id' : result.test_suite_id
        }
    else:
        data = {
            'message' : 'No test with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/tests/test_status/<int:test_status_id>", methods=['GET'])
def get_tests_by_test_status_id(test_status_id):
    logger.info("/tests_by_test_status_id/%i", test_status_id)

    tests_history = models.TestHistory.query.filter_by(test_status_id=test_status_id).all()

    if tests_history:
        data = []
        for test_history in tests_history:
            data.append( {
                'id'  : test_history.id,
                'name': test_history.test.name,
                'data': test_history.data,
                'start_datetime' : test_history.start_datetime,
                'end_datetime' : test_history.end_datetime,
                'test_status' : test_history.test_status.name,
                'test_resolution' : test_history.test_resolution.name
            })
    else:
        data = {
            'message': 'No tests were found'
        }
    
    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/tests/test_resolution/<int:test_resolution_id>", methods=['GET'])
def get_tests_by_test_resolution_id(test_resolution_id):
    logger.info("/tests_by_test_resolution_id/%i", test_resolution_id)

    tests_history = models.TestHistory.query.filter_by(test_resolution_id=test_resolution_id).all()

    if tests_history:
        data = []
        for test_history in tests_history:
            data.append( {
                'id'  : test_history.id,
                'name': test_history.test.name,
                'data': test_history.data,
                'start_datetime' : test_history.start_datetime,
                'end_datetime' : test_history.end_datetime,
                'test_status' : test_history.test_status.name,
                'test_resolution' : test_history.test_resolution.name
            })
    else:
        data = {
            'message': 'No tests were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/tests/test_suite/<int:test_suite_id>", methods=['GET'])
def get_tests_by_test_suite_id(test_suite_id):
    logger.info("/tests_by_test_suite_id/%i", test_suite_id)

    results = db.session.query(models.TestHistory, models.Test, models.TestSuite)\
        .filter(models.Test.test_suite_id == models.TestSuite.id)\
            .filter(models.TestHistory.test_id == models.Test.id)\
                .filter(models.Test.test_suite_id == test_suite_id).all()

    if results:
        data = []
        for table in results:
            test_history = table[0]
            test = table[1]
            test_suite = table[2]
            data.append( {
                'id'  : test_history.id,
                'name': test.name,
                'data': test_history.data,
                'start_datetime' : test_history.start_datetime,
                'end_datetime' : test_history.end_datetime,
                'test_status' : test_history.test_status.name,
                'test_resolution' : test_history.test_resolution.name,
                'test_suite' : test_suite.name,
                'test_type' : test_suite.name
            })
    else:
        data = {
            'message': 'No tests were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.errorhandler(404)
def notfound(error):
    data = {
        'message'  : 'The endpoint requested was not found'
    }

    resp = jsonify(data)
    resp.status_code = 404

    return resp

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=os.getenv("PORT", 5000))
