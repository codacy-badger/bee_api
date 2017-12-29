import os
import unittest

import coverage
import fixtures as _fixtures
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from bee_api import app, db, models

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

COV = coverage.coverage(
    branch=True,
    include='bee_api/*',
    omit=[
        'bee_api/tests/*',
        'config.py',
        'bee_api/*/__init__.py'
    ]
)
COV.start()


@manager.command
def tables():
    "Create database tables."
    models.create_tables(app)


@manager.command
def fixtures():
    "Install test data fixtures into the configured database."
    _fixtures.install(app, *_fixtures.all_data)


@manager.command
def test():
    """Runs the unit tests without test coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def cov():
    """Runs the unit tests with coverage."""
    tests = unittest.TestLoader().discover('project/tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
        return 0
    return 1


@manager.command
def create_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()


if __name__ == '__main__':
    manager.run()