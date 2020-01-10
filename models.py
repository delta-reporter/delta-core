from app import db
from sqlalchemy import event


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON)
    status_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Project {}>'.format(self.name)


class ProjectStatus(db.Model):
    __tablename__ = 'project_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<ProjectStatus {}>'.format(self.name)


class Launch(db.Model):
    __tablename__ = 'launches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON)
    launch_status_id = db.Column(db.Integer, db.ForeignKey('launch_status.id'),
        nullable=False)
    launch_status = db.relationship('LaunchStatus',
        backref=db.backref('launch_status', lazy=True))

    def __repr__(self):
        return '<Launch {}>'.format(self.name)


class LaunchStatus(db.Model):
    __tablename__ = 'launch_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<LaunchStatus {}>'.format(self.name)


class Test(db.Model):
    __tablename__ = 'tests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON)
    start_datetime = db.Column(db.DateTime, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('test_status.id'),
        nullable=False)
    status = db.relationship('TestStatus',
        backref=db.backref('test_status', lazy=True))
    resolution_id = db.Column(db.Integer, db.ForeignKey('test_resolution.id'),
        nullable=False)
    resolution = db.relationship('TestResolution',
        backref=db.backref('test_resolution', lazy=True))

    def __repr__(self):
        return '<Test {}>'.format(self.name)


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


class TestSuite(db.Model):
    __tablename__ = 'test_suites'

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON)
    start_datetime = db.Column(db.DateTime, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_type.id'),
        nullable=False)
    test_type = db.relationship('TestType',
        backref=db.backref('test_type', lazy=True))
    test_suite_status_id = db.Column(db.Integer, db.ForeignKey('test_suite_status.id'),
        nullable=False)
    test_suite_status = db.relationship('TestSuiteStatus',
        backref=db.backref('test_suite_status', lazy=True))


class TestType(db.Model):
    __tablename__ = 'test_type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<TestType {}>'.format(self.name)


class TestSuiteStatus(db.Model):
    __tablename__ = 'test_suite_status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return '<TestSuiteStatus {}>'.format(self.name)

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

@event.listens_for(TestType.__table__, 'after_create')
def insert_initial_test_type(*args, **kwargs):
    db.session.add(TestType(name='End to End Tests'))
    db.session.add(TestType(name='Integration Tests'))
    db.session.add(TestType(name='Unit Tests'))
    db.session.commit()

@event.listens_for(TestSuiteStatus.__table__, 'after_create')
def insert_initial_test_suite_status(*args, **kwargs):
    db.session.add(TestSuiteStatus(name='Failed'))
    db.session.add(TestSuiteStatus(name='Successful'))
    db.session.add(TestSuiteStatus(name='Running'))
    db.session.commit()
