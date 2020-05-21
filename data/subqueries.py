import models
from app import db
from sqlalchemy.sql import func


class TestCounts:

    # Subqueries to return test amounts by test run id

    total_tests_by_test_run_id = (
        db.session.query(
            models.TestHistory.test_run_id, func.count("*").label("tests_count")
        )
        .group_by(models.TestHistory.test_run_id)
        .subquery()
    )

    failed_tests_by_test_run_id = (
        db.session.query(
            models.TestHistory.test_run_id, func.count("*").label("failed_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 1)
        .group_by(models.TestHistory.test_run_id)
        .subquery()
    )

    passed_tests_by_test_run_id = (
        db.session.query(
            models.TestHistory.test_run_id, func.count("*").label("passed_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 2)
        .group_by(models.TestHistory.test_run_id)
        .subquery()
    )

    running_tests_by_test_run_id = (
        db.session.query(
            models.TestHistory.test_run_id,
            func.count("*").label("running_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 3)
        .group_by(models.TestHistory.test_run_id)
        .subquery()
    )

    incomplete_tests_by_test_run_id = (
        db.session.query(
            models.TestHistory.test_run_id,
            func.count("*").label("incomplete_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 4)
        .group_by(models.TestHistory.test_run_id)
        .subquery()
    )

    skipped_tests_by_test_run_id = (
        db.session.query(
            models.TestHistory.test_run_id,
            func.count("*").label("skipped_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 5)
        .group_by(models.TestHistory.test_run_id)
        .subquery()
    )

    # Subqueries to return test amounts by test suite history id

    total_tests_by_test_suite_history_id = (
        db.session.query(
            models.TestHistory.test_suite_history_id,
            func.count("*").label("tests_count"),
        )
        .group_by(models.TestHistory.test_suite_history_id)
        .subquery()
    )

    failed_tests_by_test_suite_history_id = (
        db.session.query(
            models.TestHistory.test_suite_history_id,
            func.count("*").label("failed_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 1)
        .group_by(models.TestHistory.test_suite_history_id)
        .subquery()
    )

    passed_tests_by_test_suite_history_id = (
        db.session.query(
            models.TestHistory.test_suite_history_id,
            func.count("*").label("passed_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 2)
        .group_by(models.TestHistory.test_suite_history_id)
        .subquery()
    )

    running_tests_by_test_suite_history_id = (
        db.session.query(
            models.TestHistory.test_suite_history_id,
            func.count("*").label("running_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 3)
        .group_by(models.TestHistory.test_suite_history_id)
        .subquery()
    )

    incomplete_tests_by_test_suite_history_id = (
        db.session.query(
            models.TestHistory.test_suite_history_id,
            func.count("*").label("incomplete_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 4)
        .group_by(models.TestHistory.test_suite_history_id)
        .subquery()
    )

    skipped_tests_by_test_suite_history_id = (
        db.session.query(
            models.TestHistory.test_suite_history_id,
            func.count("*").label("skipped_tests_count"),
        )
        .filter(models.TestHistory.test_status_id == 5)
        .group_by(models.TestHistory.test_suite_history_id)
        .subquery()
    )
