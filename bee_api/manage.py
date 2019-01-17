import sys
import os
import logging
from ast import *

from flask_script import Manager
from flask_migrate import (Migrate, MigrateCommand)
from flask_security import (SQLAlchemyUserDatastore)
from flask_security.utils import hash_password

from app import app
from classes import *
from database import (db, engine, Base)


log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


def create_countries(load_dir):
    log.info('Insert Country data in database')
    with open(os.path.join(load_dir, 'country.json'), 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db.session.add(Country(**record))
        db.session.commit()


def create_provinces(load_dir):
    log.info('Insert State data in database')
    with open(os.path.join(load_dir, 'state_province.json'), 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db.session.add(StateProvince(**record))
        db.session.commit()


def create_locations(load_dir):
    log.info('Insert Location data in database')
    with open(os.path.join(load_dir, 'location.json'), 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db.session.add(Location(**record))
        db.session.commit()


def create_roles_users():
    log.info('Insert Role data in database')
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    admin = user_datastore.find_or_create_role(name='Admin',
                                               description='Administrator')
    user_datastore.find_or_create_role(name='api', description='API user')
    user = user_datastore.create_user(email=app.config['ADMIN_EMAIL'],
                                      password=app.config['ADMIN_PASSWORD'])
    user_datastore.add_role_to_user(user, admin)
    db.session.commit()


@manager.command
def create_db():
    "Creates database and table schemas from the latest models"
    from sqlalchemy_utils import (database_exists, create_database)
    if not database_exists(engine.url):
        create_database(engine.url)
        Base.metadata.create_all(engine)
#        db.session.commit()
    else:
        print("Database already exists")


@manager.command
def drop_db():
    "Drops Database"
    from sqlalchemy_utils import (database_exists, drop_database)
    if database_exists(engine.url):
        drop_database(engine.url)
    else:
        print("Database doesn't exists")


@manager.option('-d', '--directory', help='Fixture directory, relative to this script',
                default='fixtures', dest='seed_dir')
def seed(seed_dir):
    "Loads data from fixture files"
    load_dir = os.path.join(os.path.dirname(__file__), seed_dir)
    create_countries(load_dir)
    create_provinces(load_dir)
    create_locations(load_dir)
    create_roles_users()


if __name__ == '__main__':
    manager.run()
