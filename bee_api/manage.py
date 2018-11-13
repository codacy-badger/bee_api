import sys
import os
import logging
from ast import *

from flask_script import Manager
from flask_migrate import (Migrate, MigrateCommand)
from flask_security import (SQLAlchemyUserDatastore)
from flask_security.utils import hash_password

from app import app
from database import db
from classes import *


log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

script_dir = os.path.join(os.path.dirname(__file__), 'fixtures')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

def create_countries():
    log.info('Insert Country data in database')
    with open(os.path.join(script_dir, 'country.json'), 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db.session.add(Country(**record))
        db.session.commit()


def create_provinces():
    log.info('Insert State data in database')
    with open(os.path.join(script_dir, 'state_province.json'), 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db.session.add(StateProvince(**record))
        db.session.commit()


def create_locations():
    log.info('Insert Location data in database')
    with open(os.path.join(script_dir, 'location.json'), 'r') as file:
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
    user = user_datastore.create_user(email='test@example.com',
                                      password=hash_password('test123'))
    user_datastore.add_role_to_user(user, admin)
    db.session.commit()


@manager.command
def seed():
    create_countries()
    create_provinces()
    create_locations()
    create_roles_users()


if __name__ == '__main__':
    manager.run()