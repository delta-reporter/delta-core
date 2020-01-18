import os
from logzero import logger
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import models

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
    db.session.add(models.LaunchStatus(name='Finished'))
    db.session.add(models.TestSuiteStatus(name='Failed'))
    db.session.add(models.TestSuiteStatus(name='Successful'))
    db.session.add(models.TestSuiteStatus(name='Running'))
    db.session.add(models.TestType(name='End to End Tests'))
    db.session.add(models.TestType(name='Integration Tests'))
    db.session.add(models.TestType(name='Unit Tests'))
    db.session.add(models.TestRunStatus(name='Fail'))
    db.session.add(models.TestRunStatus(name='Pass'))
    db.session.add(models.TestRunStatus(name='Running'))
    db.session.add(models.TestStatus(name='Fail'))
    db.session.add(models.TestStatus(name='Pass'))
    db.session.add(models.TestStatus(name='Running'))
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

    project = models.Project(
        name=params['name'],
        data=params['data'],
        project_status_id=params['project_status_id']
    )
    db.session.add(project)
    db.session.commit()

    data = {
        'message' : 'New project added successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_projects", methods=['POST'])
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

@app.route("/project/<int:project_id>", methods=['POST'])
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

    launch = models.Launch(
        name=params['name'],
        data=params['data'],
        launch_status_id=params['launch_status_id'],
        project_id=params['project_id']
    )
    db.session.add(launch)
    db.session.commit()

    data = {
        'message' : 'New launch added successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_launches", methods=['POST'])
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

@app.route("/launch/<int:launch_id>", methods=['POST'])
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
    logger.info("/test_run/%s", params)

    test_run = models.TestRun(
        data=params['data'],
        start_datetime=params['start_datetime'],
        end_datetime=params['end_datetime'],
        test_type_id=params['test_type_id'],
        test_run_status_id=params['test_run_status_id'],
        launch_id=params['launch_id']
    )
    db.session.add(test_run)
    db.session.commit()

    data = {
        'message' : 'New test run added successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_test_runs", methods=['POST'])
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
                'test_type' : test_run.test_type.name,
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

@app.route("/test_run/<int:test_run_id>", methods=['POST'])
def get_test_run(test_run_id):
    logger.info("/test_run/%i", test_run_id)

    result = models.TestRun.query.filter_by(id=test_run_id).first()

    if result:
        data = {
            'id'  : result.id,
            'data': result.data,
            'start_datetime' : result.start_datetime,
            'end_datetime' : result.end_datetime,
            'test_type' : result.test_type.name,
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
    logger.info("/test_suite/%s", params)

    test_suite = models.TestSuite(
        name=params['name'],
        data=params['data'],
        start_datetime=params['start_datetime'],
        end_datetime=params['end_datetime'],
        test_suite_status_id=params['test_suite_status_id'],
        test_run_id=params['test_run_id']
    )
    db.session.add(test_suite)
    db.session.commit()

    data = {
        'message' : 'New test suite added successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_test_suites", methods=['POST'])
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
                'start_datetime' : test_suite.start_datetime,
                'end_datetime' : test_suite.end_datetime,
                'test_suite_status' : test_suite.test_suite_status.name,
                'test_run' : {
                    'id' : test_suite.test_run.id,
                    'test_type' : test_suite.test_run.test_type.name,
                    'test_run_status' : test_suite.test_run.test_run_status.name,
                    'launch' : test_suite.test_run.launch.name
                    }
            })
    else:
        data = {
            'message': 'No test suites were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test_suite/<int:test_suite_id>", methods=['POST'])
def get_test_suite(test_suite_id):
    logger.info("/test_suite/%i", test_suite_id)

    result = models.TestSuite.query.filter_by(id=test_suite_id).first()

    if result:
        data = {
            'id'  : result.id,
            'name'  : result.name,
            'data': result.data,
            'start_datetime' : result.start_datetime,
            'end_datetime' : result.end_datetime,
            'test_suite_status' : result.test_suite_status.name,
            'test_run' : {
                'id' : result.test_run.id,
                'test_type' : result.test_run.test_type.name,
                'test_run_status' : result.test_run.test_run_status.name,
                'launch' : result.test_run.launch.name
                }
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
    logger.info("/test/%s", params)

    test = models.Test(
        name=params['name'],
        data=params['data'],
        start_datetime=params['start_datetime'],
        end_datetime=params['end_datetime'],
        test_status_id=params['test_status_id'],
        test_resolution_id=params['test_resolution_id'],
        test_suite_id=params['test_suite_id']
    )
    db.session.add(test)
    db.session.commit()

    data = {
        'message' : 'New test added successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/get_tests", methods=['POST'])
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
                'start_datetime' : test.start_datetime,
                'end_datetime' : test.end_datetime,
                'test_status' : test.test_status.name,
                'test_resolution' : test.test_resolution.name,
                'test_suite' : test.test_suite.name
            })
    else:
        data = {
            'message': 'No tests were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/test/<int:test_id>", methods=['POST'])
def get_test_by_test_id(test_id):
    logger.info("/test/%i", test_id)

    result = models.Test.query.filter_by(id=test_id).first()

    if result:
        data = {
            'id'  : result.id,
            'name' : result.name,
            'data': result.data,
            'start_datetime' : result.start_datetime,
            'end_datetime' : result.end_datetime,
            'test_status' : result.test_status.name,
            'test_resolution' : result.test_resolution.name,
            'test_suite' : result.test_suite.name
        }
    else:
        data = {
            'message' : 'No test with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/tests/test_status/<int:test_status_id>", methods=['POST'])
def get_tests_by_test_status_id(test_status_id):
    logger.info("/tests_by_test_status_id/%i", test_status_id)

    tests = models.Test.query.filter_by(test_status_id=test_status_id).all()

    if tests:
        data = []
        for test in tests:
            data.append( {
                'id'  : test.id,
                'name' : test.name,
                'data': test.data,
                'start_datetime' : test.start_datetime,
                'end_datetime' : test.end_datetime,
                'test_status' : test.test_status.name,
                'test_resolution' : test.test_resolution.name,
                'test_suite' : test.test_suite.name
            })
    else:
        data = {
            'message': 'No tests were found'
        }
    
    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/tests/test_resolution/<int:test_resolution_id>", methods=['POST'])
def get_tests_by_test_resolution_id(test_resolution_id):
    logger.info("/tests_by_test_resolution_id/%i", test_resolution_id)

    tests = models.Test.query.filter_by(test_resolution_id=test_resolution_id).all()

    if tests:
        data = []
        for test in tests:
            data.append( {
                'id'  : test.id,
                'name' : test.name,
                'data': test.data,
                'start_datetime' : test.start_datetime,
                'end_datetime' : test.end_datetime,
                'test_status' : test.test_status.name,
                'test_resolution' : test.test_resolution.name,
                'test_suite' : test.test_suite.name
            })
    else:
        data = {
            'message': 'No tests were found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/tests/test_suite/<int:test_suite_id>", methods=['POST'])
def get_tests_by_test_suite_id(test_suite_id):
    logger.info("/tests_by_test_suite_id/%i", test_suite_id)

    tests = models.Test.query.filter_by(test_suite_id=test_suite_id).all()

    if tests:
        data = []
        for test in tests:
            data.append( {
                'id'  : test.id,
                'name' : test.name,
                'data': test.data,
                'start_datetime' : test.start_datetime,
                'end_datetime' : test.end_datetime,
                'test_status' : test.test_status.name,
                'test_resolution' : test.test_resolution.name,
                'test_suite' : test.test_suite.name
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
