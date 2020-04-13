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


class Create:
    @staticmethod
    def initialise_status_tables():
        db.session.add(models.ProjectStatus(name="Active"))
        db.session.add(models.ProjectStatus(name="Inactive"))
        db.session.add(models.ProjectStatus(name="Archived"))
        db.session.add(models.LaunchStatus(name="Failed"))
        db.session.add(models.LaunchStatus(name="In Process"))
        db.session.add(models.LaunchStatus(name="Successful"))
        db.session.add(models.TestSuiteStatus(name="Failed"))
        db.session.add(models.TestSuiteStatus(name="Successful"))
        db.session.add(models.TestSuiteStatus(name="Running"))
        db.session.add(models.TestRunStatus(name="Failed"))
        db.session.add(models.TestRunStatus(name="Passed"))
        db.session.add(models.TestRunStatus(name="Running"))
        db.session.add(models.TestStatus(name="Failed"))
        db.session.add(models.TestStatus(name="Passed"))
        db.session.add(models.TestStatus(name="Running"))
        db.session.add(models.TestStatus(name="Incomplete"))
        db.session.add(models.TestStatus(name="Skipped"))
        db.session.add(models.TestResolution(name="Not set"))
        db.session.add(models.TestResolution(name="Working as expected"))
        db.session.add(models.TestResolution(name="Test Issue"))
        db.session.add(models.TestResolution(name="Environment Issue"))
        db.session.add(models.TestResolution(name="Application Issue"))

        db.session.commit()

        return

    @staticmethod
    def create_project(name):
        project = models.Project(
            name=name, project_status_id=constants.Constants.project_status["Active"]
        )
        db.session.add(project)
        session_commit()

        return project.id

    @staticmethod
    def create_launch(name, data, project_id):
        launch = models.Launch(
            name=name,
            data=data,
            launch_status_id=constants.Constants.launch_status["In Process"],
            project_id=project_id,
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
            test_run_status_id=constants.Constants.test_run_status["Running"],
            launch_id=launch_id,
        )
        db.session.add(test_run)
        session_commit()

        return test_run.id

    @staticmethod
    def create_test_suite(name, project_id, data, test_type):
        test_suite = models.TestSuite(
            name=name, project_id=project_id, data=data, test_type=test_type
        )
        db.session.add(test_suite)
        session_commit()

        return test_suite.id

    @staticmethod
    def create_test_suite_history(data, start_datetime, test_run_id, test_suite_id):
        test_suite_history = models.TestSuiteHistory(
            data=data,
            start_datetime=start_datetime,
            test_suite_status_id=constants.Constants.test_suite_status["Running"],
            test_run_id=test_run_id,
            test_suite_id=test_suite_id,
        )
        db.session.add(test_suite_history)
        session_commit()

        return test_suite_history.id

    @staticmethod
    def create_test(name, data, test_suite_id):
        test = models.Test(name=name, data=data, test_suite_id=test_suite_id)
        db.session.add(test)
        session_commit()

        return test.id

    @staticmethod
    def create_test_history(
        start_datetime, test_id, test_run_id, test_suite_history_id
    ):
        test_history = models.TestHistory(
            start_datetime=start_datetime,
            test_id=test_id,
            test_status_id=constants.Constants.test_status["Running"],
            test_resolution_id=constants.Constants.test_resolution["Not set"],
            test_run_id=test_run_id,
            test_suite_history_id=test_suite_history_id,
        )
        db.session.add(test_history)
        session_commit()

        return test_history.id


class Read:
    @staticmethod
    def project_by_id(project_id):
        return models.Project.query.filter_by(id=project_id).first()

    @staticmethod
    def project_by_name(project_name):
        return models.Project.query.filter_by(name=project_name).first()

    @staticmethod
    def launch_by_id(launch_id):
        return models.Launch.query.filter_by(id=launch_id).first()

    @staticmethod
    def launch_by_project_id(project_id):
        return models.Launch.query.filter_by(project_id=project_id).all()

    @staticmethod
    def test_run_by_id(test_run_id):
        return models.TestRun.query.filter_by(id=test_run_id).first()

    @staticmethod
    def test_run_by_launch_id(launch_id):
        return models.TestRun.query.filter_by(launch_id=launch_id).all()

    @staticmethod
    def test_suite_by_id(test_suite_id):
        return models.TestSuite.query.filter_by(id=test_suite_id).first()

    @staticmethod
    def test_suite_by_name_project_test_type(name, project_id, test_type):
        return models.TestSuite.query.filter_by(
            name=name, project_id=project_id, test_type=test_type
        ).first()

    @staticmethod
    def test_by_name(test_name):
        return models.Test.query.filter_by(name=test_name).first()

    @staticmethod
    def test_by_id(test_id):
        return models.Test.query.filter_by(id=test_id).first()

    @staticmethod
    def test_suite_history_by_test_run(test_run_id):
        return (
            db.session.query(models.TestRun, models.TestSuiteHistory)
            .filter(models.TestRun.id == models.TestSuiteHistory.test_run_id)
            .filter(models.TestRun.id == test_run_id)
            .all()
        )

    @staticmethod
    def test_suite_history_by_test_status_and_test_run_id(
        test_suite_status_id, test_run_id
    ):
        return (
            db.session.query(models.TestRun, models.TestSuiteHistory)
            .filter(models.TestRun.id == models.TestSuiteHistory.test_run_id)
            .filter(models.TestRun.id == test_run_id)
            .filter(
                models.TestSuiteHistory.test_suite_status_id == test_suite_status_id
            )
            .all()
        )

    @staticmethod
    def test_history_by_test_run(test_run_id):
        return (
            db.session.query(
                models.TestRun, models.TestSuiteHistory, models.TestHistory
            )
            .filter(models.TestRun.id == models.TestSuiteHistory.test_run_id)
            .filter(
                models.TestSuiteHistory.test_run_id == models.TestHistory.test_run_id
            )
            .filter(
                models.TestSuiteHistory.id == models.TestHistory.test_suite_history_id
            )
            .filter(models.TestRun.id == test_run_id)
            .all()
        )

    @staticmethod
    def test_history_by_test_status_and_test_run_id(test_status_id, test_run_id):
        return models.TestHistory.query.filter_by(
            test_status_id=test_status_id, test_run_id=test_run_id
        ).all()

    @staticmethod
    def test_history_by_test_status_id(test_status_id):
        return models.TestHistory.query.filter_by(test_status_id=test_status_id).all()

    @staticmethod
    def test_history_by_test_resolution_id(test_resolution_id):
        return models.TestHistory.query.filter_by(
            test_resolution_id=test_resolution_id
        ).all()

    @staticmethod
    def test_history_by_test_suite_id(test_suite_id):
        return (
            db.session.query(models.TestHistory, models.Test, models.TestSuite)
            .filter(models.Test.test_suite_id == models.TestSuite.id)
            .filter(models.TestHistory.test_id == models.Test.id)
            .filter(models.Test.test_suite_id == test_suite_id)
            .all()
        )


class Update:
    @staticmethod
    def update_test_history(
        test_history_id,
        end_datetime,
        trace,
        file,
        message,
        error_type,
        retries,
        test_status,
    ):
        test_history = db.session.query(models.TestHistory).get(test_history_id)
        test_history.end_datetime = end_datetime
        test_history.trace = trace
        test_history.file = file
        test_history.message = message
        test_history.error_type = error_type
        test_history.retries = retries
        test_history.test_status_id = constants.Constants.test_status.get(test_status)

        session_commit()

        return test_history.id

    @staticmethod
    def update_test_suite_history(
        test_suite_history_id, end_datetime, data, test_suite_status
    ):
        test_suite_history = db.session.query(models.TestSuiteHistory).get(
            test_suite_history_id
        )
        test_suite_history.end_datetime = end_datetime
        test_suite_history.data = data
        test_suite_history.test_suite_status_id = constants.Constants.test_suite_status.get(
            test_suite_status
        )

        session_commit()

        return test_suite_history.id

    @staticmethod
    def update_test_run(test_run_id, end_datetime, data, test_run_status):
        test_run = db.session.query(models.TestRun).get(test_run_id)
        test_run.end_datetime = end_datetime
        test_run.data = data
        test_run.test_run_status_id = constants.Constants.test_run_status.get(
            test_run_status
        )

        session_commit()

        return test_run.id
