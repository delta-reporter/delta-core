import models
import datetime
from app import db
from data import constants
from logzero import logger
from sqlalchemy import exc
from sqlalchemy.sql import func
from data.subqueries import TestCounts
import re


def session_commit():
    try:
        db.session.commit()
    except exc.SQLAlchemyError as e:
        logger.error(e)
        db.session.rollback()


class Create:
    @staticmethod
    def create_project(name, status):
        project = models.Project(
            name=name,
            project_status_id=constants.Constants.project_status["Active"]
            if not status
            else constants.Constants.project_status[status],
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
    def create_test_run(data, start_datetime, test_type, environment, launch_id):
        test_run = models.TestRun(
            data=data,
            start_datetime=start_datetime,
            test_type=test_type,
            environment=environment,
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
        test = models.MotherTest(name=name, data=data, test_suite_id=test_suite_id)
        db.session.add(test)
        session_commit()

        return test.id

    @staticmethod
    def create_test_history(
        start_datetime, test_id, test_run_id, test_suite_history_id, parameters, status
    ):
        test_history = models.Test(
            start_datetime=start_datetime,
            mother_test_id=test_id,
            test_status_id=constants.Constants.test_status["Running"]
            if not status
            else constants.Constants.test_status[status],
            test_resolution_id=constants.Constants.test_resolution["Not set"],
            test_run_id=test_run_id,
            test_suite_history_id=test_suite_history_id,
            parameters=parameters,
        )
        db.session.add(test_history)
        session_commit()

        return test_history.id

    @staticmethod
    def create_test_retry(**kwargs):
        test_retry = models.TestRetries(
            test_id=kwargs.get("test_history_id"),
            retry_count=kwargs.get("retry_count"),
            start_datetime=kwargs.get("start_datetime"),
            end_datetime=kwargs.get("end_datetime"),
            trace=kwargs.get("trace"),
            message=kwargs.get("message"),
            error_type=kwargs.get("error_type"),
            media=kwargs.get("media"),
        )
        db.session.add(test_retry)
        session_commit()

        return test_retry.id

    @staticmethod
    def store_media_file(name, type, file):
        new_file = models.Media(name=name, type=type, data=file)
        db.session.add(new_file)
        session_commit()

        return new_file.id

    @staticmethod
    def create_note(mother_test_id, note_text, added_by):
        note = models.Notes(
            mother_test_id=mother_test_id, note_text=note_text, added_by=added_by
        )
        db.session.add(note)
        session_commit()

        return note.id

    @staticmethod
    def create_smart_link(
        project_id,
        environment,
        smart_link,
        label,
        color,
        filtered,
        location,
        datetime_format,
    ):
        smart_link_element = models.SmartLinks(
            project_id=project_id,
            environment=environment,
            smart_link=smart_link,
            label=label,
            color=color,
            filtered=filtered,
            location_id=location,
            datetime_format=datetime_format,
        )
        db.session.add(smart_link_element)
        session_commit()

        return smart_link_element.id


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

        t_counts = TestCounts()

        try:
            launch = (
                db.session.query(
                    models.Launch,
                    models.TestRun,
                    t_counts.total_tests_by_test_run_id.c.tests_count,
                    t_counts.failed_tests_by_test_run_id.c.failed_tests_count,
                    t_counts.passed_tests_by_test_run_id.c.passed_tests_count,
                    t_counts.running_tests_by_test_run_id.c.running_tests_count,
                    t_counts.incomplete_tests_by_test_run_id.c.incomplete_tests_count,
                    t_counts.skipped_tests_by_test_run_id.c.skipped_tests_count,
                )
                .outerjoin(
                    t_counts.total_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.total_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.failed_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.failed_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.passed_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.passed_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.running_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.running_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.incomplete_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.incomplete_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.skipped_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.skipped_tests_by_test_run_id.c.test_run_id,
                )
                .filter(models.TestRun.launch_id == models.Launch.id)
                .filter(models.Launch.project_id == project_id)
                .order_by(models.Launch.id.desc())
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            launch = None

        return launch

    @staticmethod
    def test_run_by_id(test_run_id):
        t_counts = TestCounts()

        try:
            test_run = (
                db.session.query(
                    models.TestRun,
                    t_counts.total_tests_by_test_run_id.c.tests_count,
                    t_counts.failed_tests_by_test_run_id.c.failed_tests_count,
                    t_counts.passed_tests_by_test_run_id.c.passed_tests_count,
                    t_counts.running_tests_by_test_run_id.c.running_tests_count,
                    t_counts.incomplete_tests_by_test_run_id.c.incomplete_tests_count,
                    t_counts.skipped_tests_by_test_run_id.c.skipped_tests_count,
                )
                .outerjoin(
                    t_counts.total_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.total_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.failed_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.failed_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.passed_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.passed_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.running_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.running_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.incomplete_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.incomplete_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.skipped_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.skipped_tests_by_test_run_id.c.test_run_id,
                )
                .filter(models.TestRun.id == test_run_id)
                .order_by(models.TestRun.id)
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_run = None

        return test_run

    @staticmethod
    def simple_test_run_by_id(test_run_id):
        try:
            test_run = models.TestRun.query.filter_by(id=test_run_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_run = None

        return test_run.__dict__

    @staticmethod
    def test_run_by_launch_id(launch_id):

        t_counts = TestCounts()

        try:
            test_run = (
                db.session.query(
                    models.TestRun,
                    t_counts.total_tests_by_test_run_id.c.tests_count,
                    t_counts.failed_tests_by_test_run_id.c.failed_tests_count,
                    t_counts.passed_tests_by_test_run_id.c.passed_tests_count,
                    t_counts.running_tests_by_test_run_id.c.running_tests_count,
                    t_counts.incomplete_tests_by_test_run_id.c.incomplete_tests_count,
                    t_counts.skipped_tests_by_test_run_id.c.skipped_tests_count,
                )
                .outerjoin(
                    t_counts.total_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.total_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.failed_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.failed_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.passed_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.passed_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.running_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.running_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.incomplete_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.incomplete_tests_by_test_run_id.c.test_run_id,
                )
                .outerjoin(
                    t_counts.skipped_tests_by_test_run_id,
                    models.TestRun.id
                    == t_counts.skipped_tests_by_test_run_id.c.test_run_id,
                )
                .filter(models.TestRun.launch_id == launch_id)
                .order_by(models.TestRun.id)
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_run = None

        return test_run

    @staticmethod
    def test_runs_failed_by_launch_id(launch_id):
        try:
            failed_runs = models.TestRun.query.filter_by(
                launch_id=launch_id,
                test_run_status_id=constants.Constants.test_run_status["Failed"],
            ).all()
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
    def test_suite_history_by_suite_id_test_run(test_run_id, test_suite_id):
        try:
            test_suite_history = models.TestSuiteHistory.query.filter_by(
                test_run_id=test_run_id, test_suite_id=test_suite_id
            ).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_suite_history = None

        return test_suite_history

    @staticmethod
    def mother_test_by_name(test_name):
        try:
            mother_test = models.MotherTest.query.filter_by(name=test_name).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            mother_test = None

        return mother_test

    @staticmethod
    def test_by_id(test_id):
        try:
            test = models.Test.query.filter_by(id=test_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test = None

        return test.__dict__

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
    def test_history_by_test_id_and_test_run_id(test_id, test_run_id):
        try:
            test_history = models.Test.query.filter_by(
                mother_test_id=test_id, test_run_id=test_run_id
            ).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def test_suite_history_by_array_of_test_statuses_and_test_run_id(
        test_statuses_ids, test_run_id
    ):

        array_of_statuses = re.findall(
            "\d+", test_statuses_ids
        )  # getting all numbers from string

        t_counts = TestCounts()

        try:
            test_history = (
                db.session.query(
                    models.TestSuiteHistory,
                    t_counts.total_tests_by_test_suite_history_id.c.tests_count,
                    t_counts.failed_tests_by_test_suite_history_id.c.failed_tests_count,
                    t_counts.passed_tests_by_test_suite_history_id.c.passed_tests_count,
                    t_counts.running_tests_by_test_suite_history_id.c.running_tests_count,
                    t_counts.incomplete_tests_by_test_suite_history_id.c.incomplete_tests_count,
                    t_counts.skipped_tests_by_test_suite_history_id.c.skipped_tests_count,
                )
                .outerjoin(
                    t_counts.total_tests_by_test_suite_history_id,
                    models.TestSuiteHistory.id
                    == t_counts.total_tests_by_test_suite_history_id.c.test_suite_history_id,
                )
                .outerjoin(
                    t_counts.failed_tests_by_test_suite_history_id,
                    models.TestSuiteHistory.id
                    == t_counts.failed_tests_by_test_suite_history_id.c.test_suite_history_id,
                )
                .outerjoin(
                    t_counts.passed_tests_by_test_suite_history_id,
                    models.TestSuiteHistory.id
                    == t_counts.passed_tests_by_test_suite_history_id.c.test_suite_history_id,
                )
                .outerjoin(
                    t_counts.running_tests_by_test_suite_history_id,
                    models.TestSuiteHistory.id
                    == t_counts.running_tests_by_test_suite_history_id.c.test_suite_history_id,
                )
                .outerjoin(
                    t_counts.incomplete_tests_by_test_suite_history_id,
                    models.TestSuiteHistory.id
                    == t_counts.incomplete_tests_by_test_suite_history_id.c.test_suite_history_id,
                )
                .outerjoin(
                    t_counts.skipped_tests_by_test_suite_history_id,
                    models.TestSuiteHistory.id
                    == t_counts.skipped_tests_by_test_suite_history_id.c.test_suite_history_id,
                )
                .filter(models.TestRun.id == models.TestSuiteHistory.test_run_id)
                .filter(models.TestSuiteHistory.test_run_id == models.Test.test_run_id)
                .filter(models.TestSuiteHistory.id == models.Test.test_suite_history_id)
                .filter(models.TestRun.id == test_run_id)
                .filter(models.Test.test_status_id.in_(array_of_statuses))
                .join(models.TestSuite)
                .order_by(models.TestSuite.name.asc())
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def tests_by_array_of_test_statuses_and_test_suite_history_id(
        test_statuses_ids, test_suite_history_id
    ):

        array_of_statuses = re.findall(
            "\d+", test_statuses_ids
        )  # getting all numbers from string

        try:
            test_history = (
                db.session.query(models.Test)
                .filter(models.Test.test_suite_history_id == test_suite_history_id)
                .filter(models.Test.test_status_id.in_(array_of_statuses))
                .order_by(models.Test.id.desc())
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def test_history_by_test_resolution_id(test_resolution_id):
        try:
            test_history = models.Test.query.filter_by(
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
                db.session.query(models.Test, models.Test, models.TestSuite)
                .filter(models.MotherTest.test_suite_id == models.TestSuite.id)
                .filter(models.Test.test_id == models.MotherTest.id)
                .filter(models.MotherTest.test_suite_id == test_suite_id)
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def test_retries_by_test_history_id(test_history_id):
        try:
            test_retries = models.TestRetries.query.filter_by(
                test_history_id=test_history_id
            ).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_retries = None

        return test_retries

    @staticmethod
    def file_by_media_id(media_id):
        try:
            file_data = models.Media.query.filter_by(id=media_id).first()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()

        return file_data

    @staticmethod
    def test_history_by_test_id(test_id):
        try:
            test_history = (
                models.Test.query.filter(
                    models.Test.mother_test_id == test_id,
                    models.Test.test_status_id
                    != constants.Constants.test_status["Running"],
                )
                .order_by(models.Test.end_datetime.desc())
                .limit(10)
                .all()
            )
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            test_history = None

        return test_history

    @staticmethod
    def notes_by_mother_test_id(mother_test_id):
        try:
            notes = models.Notes.query.filter_by(mother_test_id=mother_test_id).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            notes = None

        return notes

    @staticmethod
    def smart_links_by_project_id(project_id):
        try:
            smart_links = models.SmartLinks.query.filter_by(project_id=project_id).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            smart_links = None

        return smart_links

    @staticmethod
    def smart_links_by_project_id_and_location(project_id, location):
        try:
            smart_links = models.SmartLinks.query.filter_by(
                project_id=project_id, location_id=location
            ).all()
        except exc.SQLAlchemyError as e:
            logger.error(e)
            db.session.rollback()
            smart_links = None

        return smart_links


class Update:
    @staticmethod
    def update_test_history(
        test_history_id, end_datetime, trace, file, message, error_type, test_status,
    ):
        test_history = db.session.query(models.Test).get(test_history_id)
        test_history.end_datetime = end_datetime
        test_history.trace = trace
        test_history.file = file
        test_history.message = message
        test_history.error_type = error_type
        test_history.test_status_id = constants.Constants.test_status.get(test_status)

        session_commit()

        return test_history

    @staticmethod
    def increase_test_history_retry(test_history_id):
        test_history = db.session.query(models.Test).get(test_history_id)

        test_history.retries = (
            1 if test_history.retries is None else test_history.retries + 1
        )

        session_commit()

        return test_history.retries

    @staticmethod
    def clean_test_history_media(test_history_id):
        test_history = db.session.query(models.Test).get(test_history_id)
        test_history.media = None
        session_commit()

    @staticmethod
    def update_test_history_resolution(test_id, test_resolution):
        test_history = db.session.query(models.Test).get(test_id)
        test_history.test_resolution_id = constants.Constants.test_resolution.get(
            test_resolution
        )

        session_commit()

        return test_history

    @staticmethod
    def update_general_test_resolution(mother_test_id, test_resolution):
        test = db.session.query(models.MotherTest).get(mother_test_id)
        test.test_resolution_id = constants.Constants.test_resolution.get(
            test_resolution
        )

        session_commit()

        return test

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
    def update_test_run(test_run_id, end_datetime, test_run_status):
        test_run = db.session.query(models.TestRun).get(test_run_id)
        test_run.end_datetime = end_datetime
        if test_run_status is not None:
            test_run.test_run_status_id = constants.Constants.test_run_status.get(
                test_run_status
            )

        session_commit()

        return test_run.id

    @staticmethod
    def update_test_run_data(test_run_id, data):
        test_run = db.session.query(models.TestRun).get(test_run_id)
        test_run.data = data

        session_commit()

        return test_run.id

    @staticmethod
    def update_launch(launch_id, launch_status):
        launch = db.session.query(models.Launch).get(launch_id)
        launch.launch_status_id = constants.Constants.launch_status.get(launch_status)

        session_commit()

        return launch

    @staticmethod
    def add_media_to_test_history(test_history_id, media):
        test_history = db.session.query(models.Test).get(test_history_id)

        if test_history.media:
            test_history.media.append(media)
        else:
            test_history.media = [media]

        session_commit()

        return test_history.id

    @staticmethod
    def update_test_data(test_id, data):
        test = db.session.query(models.Test).get(test_id)
        test.data = data

        session_commit()

        return test.id

    @staticmethod
    def update_project_name(id, name):
        project = db.session.query(models.Project).get(id)
        if project.name != name:
            project.name = name

        session_commit()

        return project.name

    @staticmethod
    def update_test_flaky_flag(id, is_flaky):
        test = db.session.query(models.MotherTest).get(id)
        test.is_flaky = is_flaky

        session_commit()

        return test

    @staticmethod
    def update_smart_link(id, environment, smart_link, label, color, type, location):
        smart_link_object = db.session.query(models.SmartLinks).get(id)

        smart_link_object.environment = environment
        smart_link_object.smart_link = smart_link
        smart_link_object.label = label
        smart_link_object.color = color
        smart_link_object.type_id = type
        smart_link_object.location_id = location

        session_commit()

        return smart_link_object


class Delete:

    # This is just a simple approach for deleting a project, not ready for use yet
    @staticmethod
    def delete_project(project_id):
        project = db.session.query(models.Project).get(project_id)
        if project is None:
            return "Project already deleted"
        db.session.delete(project)
        session_commit()

        return "Project deleted successfully"

    @staticmethod
    def delete_smart_link(smart_link_id):
        smart_link = db.session.query(models.SmartLinks).get(smart_link_id)
        if smart_link is None:
            return "SmartLink already deleted"
        db.session.delete(smart_link)
        session_commit()

        return "SmartLink deleted successfully"

    @staticmethod
    def delete_media_older_than_days(days):
        epoch_time = datetime.datetime.today() - datetime.timedelta(days=days)
        amount = models.Media.query.filter(
            models.Media.created_datetime <= epoch_time
        ).count()
        models.Media.query.filter(models.Media.created_datetime <= epoch_time).delete()
        db.session.commit()

        return amount
