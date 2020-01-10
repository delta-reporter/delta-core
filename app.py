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
        data=params['data']
    )
    db.session.add(project)
    db.session.commit()

    data = {
        'message'  : 'New project added successfully'
    }

    resp = jsonify(data)
    resp.status_code = 200

    return resp

@app.route("/project_status", methods=['POST'])
def project_status():
    data = {'message': 'Database updated'}

    project_status = models.ProjectStatus(
        name='active'
    )
    db.session.add(project_status)
    db.session.commit()

    return jsonify(data)

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

if __name__ == "__main__":
    app.run(host=os.getenv("HOST", "0.0.0.0"), port=os.getenv("PORT", 5000))
