from app import db
from sqlalchemy import event
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    data = db.Column(db.JSON)
    project_status_id = db.Column(db.Integer, db.ForeignKey('project_status.id'),
        nullable=False)
    project_status = db.relationship('ProjectStatus',
        backref=db.backref('project_status', lazy=True))

    def __repr__(self):
        return '<Project {}>'.format(self.name)


class ProjectStatus(db.Model):
    __tablename__ = 'project_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<ProjectStatus {}>'.format(self.name)


class Launch(db.Model):
    __tablename__ = 'launch'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    data = db.Column(db.JSON)
    launch_status_id = db.Column(db.Integer, db.ForeignKey('launch_status.id'),
        nullable=False)
    launch_status = db.relationship('LaunchStatus',
        backref=db.backref('launch_status', lazy=True))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
        nullable=False)
    project = db.relationship('Project',
        backref=db.backref('project', lazy=True))

    def __repr__(self):
        return '<Launch {}>'.format(self.name)


class LaunchStatus(db.Model):
    __tablename__ = 'launch_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<LaunchStatus {}>'.format(self.name)


class TestRun(db.Model):
    __tablename__ = 'test_run'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    test_type = db.Column(db.String(100), nullable=False)
    test_run_status_id = db.Column(db.Integer, db.ForeignKey('test_run_status.id'),
        nullable=False)
    test_run_status = db.relationship('TestRunStatus',
        backref=db.backref('test_run_status', lazy=True))
    launch_id = db.Column(db.Integer, db.ForeignKey('launch.id'),
        nullable=False)
    launch = db.relationship('Launch',
        backref=db.backref('launch', lazy=True))

    def __repr__(self):
        return '<TestRun {}>'.format(self.id)


class TestRunStatus(db.Model):
    __tablename__ = 'test_run_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<TestRunStatus {}>'.format(self.name)


class TestSuite(db.Model):
    __tablename__ = 'test_suite'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    data = db.Column(db.JSON)
    test_type = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'),
        nullable=False)


class TestSuiteHistory(db.Model):
    __tablename__ = 'test_suite_history'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    test_suite_status_id = db.Column(db.Integer, db.ForeignKey('test_suite_status.id'),
        nullable=False)
    test_suite_status = db.relationship('TestSuiteStatus',
        backref=db.backref('test_suite_status', lazy=True))
    test_run_id = db.Column(db.Integer, db.ForeignKey('test_run.id'),
        nullable=False)
    test_run = db.relationship('TestRun',
        backref=db.backref('test_run', lazy=True))
    test_suite_id = db.Column(db.Integer, db.ForeignKey('test_suite.id'),
        nullable=False)
    test_suite = db.relationship('TestSuite',
        backref=db.backref('test_suite', lazy=True))


class TestSuiteStatus(db.Model):
    __tablename__ = 'test_suite_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<TestSuiteStatus {}>'.format(self.name)


class Test(db.Model):
    __tablename__ = 'test'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    data = db.Column(db.JSON)
    test_suite_id = db.Column(db.Integer, db.ForeignKey('test_suite.id'),
        nullable=False)

    def __repr__(self):
        return '<Test {}>'.format(self.name)


class TestHistory(db.Model):
    __tablename__ = 'test_history'

    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    trace = db.Column(db.String)
    file = db.Column(db.String(2000))
    retries = db.Column(db.Integer)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'),
        nullable=False)
    test = db.relationship('Test',
        backref=db.backref('test', lazy=True))
    test_status_id = db.Column(db.Integer, db.ForeignKey('test_status.id'),
        nullable=False)
    test_status = db.relationship('TestStatus',
        backref=db.backref('test_status', lazy=True))
    test_resolution_id = db.Column(db.Integer, db.ForeignKey('test_resolution.id'),
        nullable=False)
    test_resolution = db.relationship('TestResolution',
        backref=db.backref('test_resolution', lazy=True))
    test_run_id = db.Column(db.Integer, db.ForeignKey('test_run.id'),
        nullable=False)
    test_suite_history_id = db.Column(db.Integer, db.ForeignKey('test_suite_history.id'),
        nullable=False)

    def __repr__(self):
        return '<TestHistory {}>'.format(self.id)


class TestStatus(db.Model):
    __tablename__ = 'test_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<TestStatus {}>'.format(self.name)


class TestResolution(db.Model):
    __tablename__ = 'test_resolution'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<TestResolution {}>'.format(self.name)


#TODO:
#   All these event are actually not executed
#   Will need to check for a better way to
#   initialize our data
#  

@event.listens_for(ProjectStatus.__table__, 'after_create')
def insert_initial_project_status(*args, **kwargs):
    db.session.add(ProjectStatus(name='Active'))
    db.session.add(ProjectStatus(name='Inactive'))
    db.session.add(ProjectStatus(name='Archived'))
    db.session.commit()

@event.listens_for(LaunchStatus.__table__, 'after_create')
def insert_initial_launch_status(*args, **kwargs):
    db.session.add(LaunchStatus(name='Failed'))
    db.session.add(LaunchStatus(name='In Process'))
    db.session.add(LaunchStatus(name='Finished'))
    db.session.commit()

@event.listens_for(TestRunStatus.__table__, 'after_create')
def insert_initial_test_type(*args, **kwargs):
    db.session.add(TestRunStatus(name='Success'))
    db.session.add(TestRunStatus(name='Failed'))
    db.session.add(TestRunStatus(name='Running'))
    db.session.commit()

@event.listens_for(TestSuiteStatus.__table__, 'after_create')
def insert_initial_test_suite_status(*args, **kwargs):
    db.session.add(TestSuiteStatus(name='Failed'))
    db.session.add(TestSuiteStatus(name='Successful'))
    db.session.add(TestSuiteStatus(name='Running'))
    db.session.commit()

@event.listens_for(TestStatus.__table__, 'after_create')
def insert_initial_test_status(*args, **kwargs):
    db.session.add(TestStatus(name='Fail'))
    db.session.add(TestStatus(name='Pass'))
    db.session.add(TestStatus(name='Running'))
    db.session.commit()

@event.listens_for(TestResolution.__table__, 'after_create')
def insert_initial_test_resolution(*args, **kwargs):
    db.session.add(TestResolution(name='Test Issue'))
    db.session.add(TestResolution(name='Environment Issue'))
    db.session.add(TestResolution(name='Application Issue'))
    db.session.commit()
