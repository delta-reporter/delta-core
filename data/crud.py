import models
from app import db
from data import constants
from logzero import logger
from sqlalchemy import exc


def session_commit():
    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        logger.error(e)
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

        session_commit()

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
    def projects():
        try:
            projects = models.Project.query.all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            projects = None

        return projects

    @staticmethod
    def project_by_id(project_id):
        try:
            project = models.Project.query.filter_by(id=project_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            project = None

        return project

    @staticmethod
    def project_by_name(project_name):
        try:
            project = models.Project.query.filter_by(name=project_name).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            project = None

        return project

    @staticmethod
    def launch_by_id(launch_id):
        try:
            launch = models.Launch.query.filter_by(id=launch_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            launch = None

        return launch

    @staticmethod
    def launch_by_project_id(project_id):
        try:
            launch = models.Launch.query.filter_by(project_id=project_id).order_by(models.Launch.id.desc()).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            launch = None

        return launch

    @staticmethod
    def test_run_by_id(test_run_id):
        try:
            test_run = models.TestRun.query.filter_by(id=test_run_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_run = None

        return test_run

    @staticmethod
    def test_run_by_launch_id(launch_id):
        try:
            test_run = models.TestRun.query.filter_by(launch_id=launch_id).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_run = None

        return test_run

    @staticmethod
    def test_runs_failed_by_launch_id(launch_id):
        try:
            failed_runs = models.TestRun.query.filter_by(launch_id=launch_id, test_run_status_id=constants.Constants.test_run_status["Failed"]).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            failed_runs = None

        return failed_runs

    @staticmethod
    def test_suite_by_id(test_suite_id):
        try:
            test_suite = models.TestSuite.query.filter_by(id=test_suite_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_suite = None

        return test_suite

    @staticmethod
    def test_suite_by_name_project_test_type(name, project_id, test_type):
        try:
            test_suite = models.TestSuite.query.filter_by(
                name=name, project_id=project_id, test_type=test_type
            ).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_suite = None

        return test_suite

    @staticmethod
    def test_by_name(test_name):
        try:
            test =  models.Test.query.filter_by(name=test_name).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test = None

        return test

    @staticmethod
    def test_by_id(test_id):
        try:
            test = models.Test.query.filter_by(id=test_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test = None

        return test

    @staticmethod
    def test_suite_history_by_test_run(test_run_id):
        try:
            test_suite_history = (
                db.session.query(models.TestRun, models.TestSuiteHistory)
                .filter(models.TestRun.id == models.TestSuiteHistory.test_run_id)
                .filter(models.TestRun.id == test_run_id)
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_suite_history = None

        return test_suite_history

    @staticmethod
    def test_suite_history_by_test_status_and_test_run_id(
        test_suite_status_id, test_run_id
    ):
        try:
            test_suite_history = (
                db.session.query(models.TestRun, models.TestSuiteHistory)
                .filter(models.TestRun.id == models.TestSuiteHistory.test_run_id)
                .filter(models.TestRun.id == test_run_id)
                .filter(
                    models.TestSuiteHistory.test_suite_status_id == test_suite_status_id
                )
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_suite_history = None

        return test_suite_history

    @staticmethod
    def test_history_by_test_run(test_run_id):
        try:
            test_history = (
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
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def test_history_by_test_status_and_test_run_id(test_status_id, test_run_id):
        try:
            test_history = models.TestHistory.query.filter_by(
                test_status_id=test_status_id, test_run_id=test_run_id
            ).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def test_history_by_test_status_id(test_status_id):
        try:
            test_history = models.TestHistory.query.filter_by(test_status_id=test_status_id).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def test_history_by_test_resolution_id(test_resolution_id):
        try:
            test_history = models.TestHistory.query.filter_by(
                test_resolution_id=test_resolution_id
            ).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def test_history_by_test_suite_id(test_suite_id):
        try:
            test_history = (
                db.session.query(models.TestHistory, models.Test, models.TestSuite)
                .filter(models.Test.test_suite_id == models.TestSuite.id)
                .filter(models.TestHistory.test_id == models.Test.id)
                .filter(models.Test.test_suite_id == test_suite_id)
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history


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
    def update_test_history_resolution(test_history_id, test_resolution):
        test_history = db.session.query(models.TestHistory).get(test_history_id)
        test_history.test_resolution_id = constants.Constants.test_resolution.get(test_resolution)

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

    @staticmethod
    def update_launch(launch_id, launch_status):
        launch = db.session.query(models.Launch).get(launch_id)
        launch.launch_status_id = constants.Constants.launch_status.get(
            launch_status
        )

        session_commit()

        return launch.id
