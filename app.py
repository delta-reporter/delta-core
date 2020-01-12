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
    db.session.add(models.TestStatus(name='Fail'))
    db.session.add(models.TestStatus(name='Pass'))
    db.session.add(models.TestStatus(name='Running'))
    db.session.add(models.TestResolution(name='Test Issue'))
    db.session.add(models.TestResolution(name='Environment Issue'))
    db.session.add(models.TestResolution(name='Application Issue'))
    db.session.add(models.TestType(name='End to End Tests'))
    db.session.add(models.TestType(name='Integration Tests'))
    db.session.add(models.TestType(name='Unit Tests'))
    db.session.add(models.TestSuiteStatus(name='Failed'))
    db.session.add(models.TestSuiteStatus(name='Successful'))
    db.session.add(models.TestSuiteStatus(name='Running'))
    db.session.commit()

    data = {
        'message'  : 'Database initialized successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/projects", methods=['POST'])
def projects():
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
        'message'  : 'New project added successfully'
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
                'id'  : project.id,
                'name': project.name,
                'data': project.data,
                'project_status': project.project_status.name
            })
    else:
        data = {
            'message': 'No project with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/project/<int:project_id>", methods=['POST'])
def project(project_id):
    logger.info("/project/%i", project_id)

    result = models.Project.query.filter_by(id=project_id).first()

    if result:
        data = {
            'id'  : result.id,
            'name': result.name,
            'data': result.data,
            'project_status': result.project_status.name
        }
    else:
        data = {
            'message': 'No project with the id provided was found'
        }

    resp = jsonify(data)
    resp.status_code = 200

    return resp


@app.route("/launches", methods=['POST'])
def launches():
    data = {'id': 0, 'name': 'Release Zero', 'changelog': '- Added rabbits\n- More cats'}
    return jsonify(data)

@app.route("/test_suites", methods=['POST'])
def testsuites():
    data = {'id': 0, 'title': 'Test Zero', 'test_type': 'integration', 'status': 'PASS', 'duration': '3 minutes 23 seconds', 'start': 'timestamp', 'end': 'timestamp'}
    return jsonify(data)

@app.route("/tests", methods=['POST'])
def tests():
    data = {'id': 0, 'suite_id': 0, 'launch_id': 0, 'title': "Test Zero", 'status': 'PASS', 'duration': '3 minutes 23 seconds', 'start': 'timestamp', 'end': 'timestamp', 'screenshots': ['s3://whatever0','s3://whatever1']}
    return jsonify(data)

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
