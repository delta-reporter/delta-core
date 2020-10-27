from app import db
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableList, MutableDict

Base = declarative_base()


class Project(db.Model):
    __tablename__ = "project"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    data = db.Column(MutableDict.as_mutable(db.JSON))
    project_status_id = db.Column(
        db.Integer, db.ForeignKey("project_status.id"), nullable=False
    )
    project_status = db.relationship(
        "ProjectStatus", backref=db.backref("project_status", lazy=True)
    )

    def __repr__(self):
        return "<Project {}>".format(self.name)


class ProjectStatus(db.Model):
    __tablename__ = "project_status"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<ProjectStatus {}>".format(self.name)


class Launch(db.Model):
    __tablename__ = "launch"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    data = db.Column(MutableDict.as_mutable(db.JSON))
    launch_status_id = db.Column(
        db.Integer, db.ForeignKey("launch_status.id"), nullable=False
    )
    launch_status = db.relationship(
        "LaunchStatus", backref=db.backref("launch_status", lazy=True)
    )
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    project = db.relationship("Project", backref=db.backref("project", lazy=True))

    def __repr__(self):
        return "<Launch {}>".format(self.name)


class LaunchStatus(db.Model):
    __tablename__ = "launch_status"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<LaunchStatus {}>".format(self.name)


class TestRun(db.Model):
    __tablename__ = "test_run"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(MutableDict.as_mutable(db.JSON))
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    test_type = db.Column(db.String(100), nullable=False)
    test_run_status_id = db.Column(
        db.Integer, db.ForeignKey("test_run_status.id"), nullable=False
    )
    test_run_status = db.relationship(
        "TestRunStatus", backref=db.backref("test_run_status", lazy=True)
    )
    launch_id = db.Column(db.Integer, db.ForeignKey("launch.id"), nullable=False)
    launch = db.relationship("Launch", backref=db.backref("launch", lazy=True))

    def __repr__(self):
        return "<TestRun {}>".format(self.id)


class TestRunStatus(db.Model):
    __tablename__ = "test_run_status"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<TestRunStatus {}>".format(self.name)


class TestSuite(db.Model):
    __tablename__ = "test_suite"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(MutableDict.as_mutable(db.JSON))
    test_type = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)


class TestSuiteHistory(db.Model):
    __tablename__ = "test_suite_history"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(MutableDict.as_mutable(db.JSON))
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    test_suite_status_id = db.Column(
        db.Integer, db.ForeignKey("test_suite_status.id"), nullable=False
    )
    test_suite_status = db.relationship(
        "TestSuiteStatus", backref=db.backref("test_suite_status", lazy=True)
    )
    test_run_id = db.Column(db.Integer, db.ForeignKey("test_run.id"), nullable=False)
    test_run = db.relationship("TestRun", backref=db.backref("test_run", lazy=True))
    test_suite_id = db.Column(
        db.Integer, db.ForeignKey("test_suite.id"), nullable=False
    )
    test_suite = db.relationship(
        "TestSuite", backref=db.backref("test_suite", lazy=True)
    )


class TestSuiteStatus(db.Model):
    __tablename__ = "test_suite_status"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<TestSuiteStatus {}>".format(self.name)


class MotherTest(db.Model):
    __tablename__ = "mother_test"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    data = db.Column(MutableDict.as_mutable(db.JSON))
    test_suite_id = db.Column(
        db.Integer, db.ForeignKey("test_suite.id"), nullable=False
    )
    test_resolution_id = db.Column(
        db.Integer, db.ForeignKey("test_resolution.id"))
    is_flaky = db.Column(db.Boolean())

    def __repr__(self):
        return "<MotherTest {}>".format(self.name)


class Test(db.Model):
    __tablename__ = "test"

    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    trace = db.Column(db.String)
    file = db.Column(db.String(2000))
    message = db.Column(db.String(2000))
    error_type = db.Column(db.String(2000))
    retries = db.Column(db.Integer)
    parameters = db.Column(db.String(3000))
    media = db.Column(MutableList.as_mutable(db.JSON))
    mother_test_id = db.Column(
        db.Integer, db.ForeignKey("mother_test.id"), nullable=False
    )
    mother_test = db.relationship(
        "MotherTest", backref=db.backref("mother_test", lazy=True)
    )
    test_status_id = db.Column(
        db.Integer, db.ForeignKey("test_status.id"), nullable=False
    )
    test_status = db.relationship(
        "TestStatus", backref=db.backref("test_status", lazy=True)
    )
    test_resolution_id = db.Column(
        db.Integer, db.ForeignKey("test_resolution.id"), nullable=False
    )
    test_resolution = db.relationship(
        "TestResolution", backref=db.backref("test_resolution", lazy=True)
    )
    test_run_id = db.Column(db.Integer, db.ForeignKey("test_run.id"), nullable=False)
    test_suite_history_id = db.Column(
        db.Integer, db.ForeignKey("test_suite_history.id"), nullable=False
    )

    def __repr__(self):
        return "<Test {}>".format(self.id)


class TestStatus(db.Model):
    __tablename__ = "test_status"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<TestStatus {}>".format(self.name)


class TestResolution(db.Model):
    __tablename__ = "test_resolution"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return "<TestResolution {}>".format(self.name)


class TestRetries(db.Model):
    __tablename__ = "test_retries"

    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey("test.id"), nullable=False)
    retry_count = db.Column(db.Integer)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    trace = db.Column(db.String)
    message = db.Column(db.String(2000))
    error_type = db.Column(db.String(2000))
    media = db.Column(MutableList.as_mutable(db.JSON))

    def __repr__(self):
        return "<TestRetries {}>".format(self.id)


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    type = db.Column(db.String(120))
    data = db.Column(db.LargeBinary)
    created_datetime = db.Column(db.DateTime(timezone=True), server_default=func.now())

class Notes(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    mother_test_id = db.Column(db.Integer, db.ForeignKey("mother_test.id"), nullable=False)
    note_text = db.Column(db.String(2000))
    created_datetime = db.Column(db.DateTime(timezone=True), server_default=func.now())
    added_by = db.Column(db.String(200))