import models
from app import db
from data import constants
from logzero import logger
from sqlalchemy import exc

def session_commit():
    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        logger.warning(e)
        db.session.rollback()

class Create():

    @staticmethod
    def create_project(name):
        project = models.Project(
            name=name,
            project_status_id=constants.Constants.project_status['Active']
        )
        db.session.add(project)
        session_commit()

        return project.id

    @staticmethod
    def create_launch(name, data, project_id):
        launch = models.Launch(
            name=name,
            data=data,
            launch_status_id=constants.Constants.launch_status['In Process'],
            project_id=project_id
        )
        db.session.add(launch)
        session_commit()

        return launch.id

    @staticmethod
    def create_test_run(data, start_datetime, test_type, launch_id):
        test_run = models.TestRun(
            data=data,
            start_datetime=start_datetime,
            test_type=test_type,
            test_run_status_id=constants.Constants.test_run_status['Running'],
            launch_id=launch_id
        )
        db.session.add(test_run)
        session_commit()

        return test_run.id

    @staticmethod
    def create_test_suite(name, data, test_type):
        test_suite = models.TestSuite(
            name=name,
            data=data,
            test_type=test_type
        )
        db.session.add(test_suite)
        session_commit()

        return test_suite.id

    @staticmethod
    def create_test_suite_history(data, start_datetime, test_run_id, test_suite_id):
        test_suite_history = models.TestSuiteHistory(
            data=data,
            start_datetime=start_datetime,
            test_suite_status_id=constants.Constants.test_suite_status['Running'],
            test_run_id=test_run_id,
            test_suite_id=test_suite_id
        )
        db.session.add(test_suite_history)
        session_commit()

        return test_suite_history.id

    @staticmethod
    def create_test(name, data, test_suite_id):
        test = models.Test(
            name=name,
            data=data,
            test_suite_id=test_suite_id
        )
        db.session.add(test)
        session_commit()

        return test.id

    @staticmethod
    def create_test_history(start_datetime, data, test_id, test_run_id):
        test_history = models.TestHistory(
            start_datetime=start_datetime,
            data=data,
            test_id=test_id,
            test_status_id=constants.Constants.test_status['Running'],
            test_resolution_id=constants.Constants.test_resolution['Not set'],
            test_run_id=test_run_id
        )
        db.session.add(test_history)
        session_commit()

        return test_history.id


class Update():

    @staticmethod
    def update_test_history(test_history_id, end_datetime, data, test_status):
        test_history = db.session.query(models.TestHistory).get(test_history_id)
        test_history.end_datetime = end_datetime
        test_history.data = data
        test_history.test_status_id = constants.Constants.test_status.get(test_status)

        session_commit()

        return test_history.id

    @staticmethod
    def update_test_suite_history(test_suite_history_id, end_datetime, data, test_suite_status):
        test_suite_history = db.session.query(models.TestSuiteHistory).get(test_suite_history_id)
        test_suite_history.end_datetime = end_datetime
        test_suite_history.data = data
        test_suite_history.test_suite_status_id = constants.Constants.test_suite_status.get(test_suite_status)
        
        session_commit()

        return test_suite_history.id

    @staticmethod
    def update_test_run(test_run_id, end_datetime, data, test_run_status):
        test_run = db.session.query(models.TestRun).get(test_run_id)
        test_run.end_datetime = end_datetime
        test_run.data = data
        test_run.test_run_status_id = constants.Constants.test_run_status.get(test_run_status)
        
        session_commit()

        return test_run.id
