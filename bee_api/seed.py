import sys
import logging
from ast import literal_eval
from bee_api.database import db_session
from bee_api.models import (Country, StateProvince, Location, Role, User)
from bee_api.app import bee_api
from flask_security import SQLAlchemyUserDatastore, Security
from flask_security.utils import hash_password
from bee_api import db

log = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_countries():
    log.info('Insert Country data in database')
    with open('fixtures/country.json', 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db_session.add(Country(**record))
        db_session.commit()

def create_provinces():
    log.info('Insert State data in database')
    with open('fixtures/state_province.json', 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db_session.add(StateProvince(**record))
        db_session.commit()

def create_locations():
    log.info('Insert Location data in database')
    with open('fixtures/location.json', 'r') as file:
        data = literal_eval(file.read())
        for record in data:
            db_session.add(Location(**record))
        db_session.commit()

def create_roles_users():
    log.info('Insert Role data in database')
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(bee_api, user_datastore)
    admin = user_datastore.find_or_create_role(name='Admin',
                                               description='Administrator')
    user_datastore.find_or_create_role(name='api', description='API user')
    user = user_datastore.create_user(email='test@example.com',
                                      password=hash_password('test123'))
    user_datastore.add_role_to_user(user, admin)
    db.session.commit()


def main():
    with bee_api.app_context():
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        create_countries()
        create_provinces()
        create_locations()
        create_roles_users()


if __name__ == '__main__':
    main()