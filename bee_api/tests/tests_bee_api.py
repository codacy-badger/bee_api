import os
import glob
import json
from flask_fixtures import load_fixtures
from flask_fixtures.loaders import JSONLoader
from app import app
from database import db
from classes import User, Role
from datetime import datetime

import unittest

os.environ['APP_SETTINGS'] = 'bee_api.config.TestingConfig'


class BeeWebTestCase(unittest.TestCase):
    def create_user_token(self, account={'email': 'joe@gmail.com',
                                         'password': 'test'},
                                roles='user'):
        if 'firstName' in account:
            firstName = account['firstName']
        else:
            firstName = None
        if 'lastName' in account:
            lastName = account['lastName']
        else:
            lastName = None
        if 'phoneNumber' in account:
            phoneNumber = account['phoneNumber']
        else:
            phoneNumber = None
        if 'api' in account:
            api = account['api']
        else:
            api = None
        role = Role.query.filter_by(name=roles).first()

        user = User(
            email=account['email'],
            password=account['password'],
            firstName=firstName,
            lastName=lastName,
            phoneNumber=phoneNumber,
            roleId=role.id,
            api=api
        )
        db.session.add(user)
        db.session.commit()
        if api is None:
            with self.app:
                resp_login = self.app.post(
                    '/auth/login',
                    data=json.dumps(dict(
                    email=account['email'],
                    password=account['password']
                    )),
                content_type='application/json'
                )
        else:
            with self.app:
                resp_login = self.app.post(
                    '/auth/api',
                    data=json.dumps(dict(
                        api=api
                    )),
                content_type='application/json'
            )
        return resp_login

    def setUp(self):
        app_settings = os.getenv(
            'APP_SETTINGS',
            'bee_api.config.TestingConfig'
        )
        app.config.from_object(app_settings)

        fixture_files = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..','fixtures','*json')

        with app.app_context():
            db.create_all()
            for fixture_file in glob.glob(fixture_files):
                fixtures = JSONLoader().load(fixture_file)
                load_fixtures(db, fixtures)

        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
#        with bee_api.app_context():
#            db.drop_all()
#            os.close(self.db_fd)
#            os.unlink(os.path.join(classes.config.basedir,
#                                   classes.config.database_name))

    def test_get_all_countries(self):
        rv = self.app.get('/countries')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(len(json_resp['countries']), 3)
        self.assertEqual(json_resp['countries'][0]['name'], 'United States')
        self.assertEqual(json_resp['countries'][0]['id'], 1)

    def test_get_country(self):
        rv = self.app.get('/countries/2')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(len(json_resp),1)
        self.assertEqual(json_resp['countries']['name'], 'Canada')
        self.assertEqual(json_resp['countries']['id'], 2)

#    def test_add_country(self):
#        rv = self.classes.post('/countries/',
#                           content_type='application/json',
#                           data=json.dumps(dict(name='West Germany')))

#        self.assertEqual(rv.status_code, 200)

#        rv = self.classes.post('/countries/',
#                           content_type='application/json',
#                           data=json.dumps({'name':'West Germany'}))

#        self.assertEqual(rv.status_code, 409)

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email"""
        user = User(
            email='joe@gmail.com',
            password='test',
            firstName='Joe'
        )
        db.session.add(user)
        db.session.commit()
        with self.app:
            response = self.app.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(
                data['message'] == 'User already exists. Please Log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    def test_registered_user_min(self):
        """ Test for login of registered-user login """
        with self.app:
            # user registration
            resp_register = self.app.post(
                '/auth/register',
                data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456'
                )),
                content_type='application/json',
            )
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)

    def test_registered_user_max(self):
        with self.app:
            resp_register = self.app.post(
                '/auth/register',
                    data=json.dumps(dict(
                    email='joe@gmail.com',
                    password='123456',
                    firstName='Joe',
                    lastName='Plumber',
                    roles='admin',
                    locationId=1,
                    phoneNumber="123-235-1111"
                )),
                content_type='application/json',
            )
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(
                data_register['message'] == 'Successfully registered.'
            )
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)

    def test_login_logout_user(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user)
        data = json.loads(response.data.decode())

        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully logged in.')
        self.assertTrue(data['auth_token'])
        self.assertTrue(response.content_type == 'application/json')
        self.assertEqual(response.status_code, 200)

        response = self.app.post(
                '/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + data['auth_token']
                )
            )
        self.assertEqual(response.status_code, 401)

    def test_get_all_statesprovinces_api(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123',
                'api': 'thisisatestofapi'}
        response = self.create_user_token(account=user)
        data = json.loads(response.data.decode())

        rv = self.app.get('/state-provinces')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)

        self.assertEqual(len(json_resp['stateprovinces']), 50)
        self.assertEqual(json_resp['stateprovinces'][0]['name'], 'Alabama')
        self.assertEqual(json_resp['stateprovinces'][0]['country']['id'], 1)
        self.assertEqual(json_resp['stateprovinces'][0]['country']['name'],
                         'United States')
        self.assertEqual(json_resp['stateprovinces'][0]['abbreviation'], 'AL')

    def test_get_all_statesprovinces(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
#        response = self.create_user_token(account=user)
#        data = json.loads(response.data.decode())

        rv = self.app.get('/state-provinces')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)

        self.assertEqual(len(json_resp['stateprovinces']), 50)
        self.assertEqual(json_resp['stateprovinces'][0]['name'], 'Alabama')
        self.assertEqual(json_resp['stateprovinces'][0]['country']['id'], 1)
        self.assertEqual(json_resp['stateprovinces'][0]['country']['name'],
                         'United States')
        self.assertEqual(json_resp['stateprovinces'][0]['abbreviation'], 'AL')

    def test_get_statesprovinces(self):
        rv = self.app.get('/state-provinces/21')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)

        self.assertEqual(len(json_resp), 1)
        self.assertEqual(json_resp['stateprovinces']['name'], 'Massachusetts')
        self.assertEqual(json_resp['stateprovinces']['country']['id'],1)
        self.assertEqual(json_resp['stateprovinces']['abbreviation'], 'MA')
        self.assertEqual(json_resp['stateprovinces']['location'][0]['id'], 1)
        self.assertEqual(json_resp['stateprovinces']['location'][0]['city'],
                         'Boston')
        self.assertEqual(json_resp['stateprovinces']['location'][0]
                         ['streetAddress'],'123 Main St.')

    def test_add_stateprovinces_no_admin(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user)
        data = json.loads(response.data.decode())
        json_data = dict(name="Quebec", abbreviation="QC",
                     country=dict(name="Canada", id=2))
        rv = self.app.post('/state-provinces',
                           data = json.dumps(json_data),
                           content_type='application/json',
                           headers=dict(
                               Authorization='Bearer ' + data['auth_token'])
                           )
        self.assertEqual(rv.status_code, 403)

    def test_add_stateprovinces(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user, roles='admin')
        data = json.loads(response.data.decode())
        json_data = dict(name="Quebec", abbreviation="QC",
                     country=dict(name="Canada", id=2))
        rv = self.app.post('/state-provinces',
                           data = json.dumps(json_data),
                           content_type='application/json',
                           headers=dict(
                               Authorization='Bearer ' + data['auth_token'])
                           )
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['stateprovinces']['abbreviation'], 'QC')
        self.assertEqual(json_resp['stateprovinces']['name'], 'Quebec')
        self.assertEqual(json_resp['stateprovinces']['country']['id'], 2)

        json_data = dict(name="Quebec", abbreviation="QC",
                     country=dict(name="Canada", id=2))

        rv = self.app.post('/state-provinces',
                           data = json.dumps(json_data),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 401)

    def test_add_location(self):
        rv = self.app.post('/locations',
                           content_type='application/json',
                           data=json.dumps(dict(city='Hanover',
                                streetAddress='84 Summer St.',
                                stateProvince=dict(name='Massachusetts', id=21))))

        self.assertEqual(rv.status_code, 200)

    def test_get_all_locations(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user, roles='admin')
        data = json.loads(response.data.decode())

        rv = self.app.get('/locations',
                          headers=dict(
                              Authorization='Bearer ' + data['auth_token'])
                          )
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['locations'][0]['city'], 'Boston')
        self.assertEqual(json_resp['locations'][0]['id'], 1)
        self.assertEqual(json_resp['locations'][0]['streetAddress'], '123 Main St.')

        json_resp = json.loads(rv.data)

    def test_get_locations(self):
        rv = self.app.get('/locations/1')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['locations']['city'], 'Boston')
        self.assertEqual(json_resp['locations']['id'], 1)
        self.assertEqual(json_resp['locations']['streetAddress'], '123 Main St.')

    def test_no_user(self):
        rv = self.app.get('/users/111')
        self.assertEqual(rv.status_code, 401)

    def test_get_user_no_admin(self):
        rv = self.app.get('/users/1')
        self.assertEqual(rv.status_code, 401)

    def test_get_user_forbidden(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user)
        data = json.loads(response.data.decode())
        rv = self.app.get('/users/1',
                          headers=dict(
                              Authorization='Bearer ' + data['auth_token']
                          )
                          )
        self.assertEqual(rv.status_code, 403)


    def test_get_user_same_user(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123',
                'firstName': 'Joe', 'lastName': 'Plumber',
                'phoneNumber': '123456789'}
        response = self.create_user_token(account=user)
        data = json.loads(response.data.decode())
        rv = self.app.get('/users/2',
                          headers=dict(
                              Authorization='Bearer ' + data['auth_token']
                          )
                          )
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['users']['firstName'], user['firstName'])
        self.assertEqual(json_resp['users']['lastName'], user['lastName'])
        self.assertEqual(json_resp['users']['email'], user['email'])
        self.assertEqual(json_resp['users']['phoneNumber'],
                         user['phoneNumber'])


    def test_get_user_admin(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user, roles='admin')
        data = json.loads(response.data.decode())
        rv = self.app.get('/users/1',
                          headers=dict(
                              Authorization='Bearer ' + data['auth_token']
                          )
                          )
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['users']['firstName'], 'Mickey')
        self.assertEqual(json_resp['users']['lastName'], 'Mouse')
        self.assertEqual(json_resp['users']['email'], 'mm@disney.com')
        self.assertEqual(json_resp['users']['location']['city'], 'Boston')
        self.assertEqual(json_resp['users']['location']['id'], 1)
        self.assertEqual(json_resp['users']['location']['streetAddress'],
                         '123 Main St.')
        self.assertEqual(json_resp['users']['phoneNumber'],
                         '7812175265')


    def test_add_hivedata(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user)
        data = json.loads(response.data.decode())

        json_data = dict(probes=[
                            dict(humidity = 10.5, temperature = 78.5,
                            outdoor = False, sensor = 11),
                            dict(humidity=20.5, temperature=88.5,
                            outdoor=True, sensor=22)
                            ], hive=dict(id=1),
                            dateCreated=datetime.utcnow().__str__())
        rv = self.app.post('/hivedata/',
                           data = json.dumps(json_data),
                           content_type='application/json',
                           headers=dict(
                               Authorization='Bearer ' + data['auth_token'])
                           )
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['message'], 'Updated Hive Data')


    def test_index(self):
        user = {'email': 'joe@gmail.com', 'password': 'test123'}
        response = self.create_user_token(account=user)
        data = json.loads(response.data.decode())
        rv = self.app.get('/',
                          headers=dict(
                              Authorization='Bearer ' + data['auth_token']
                          )
                          )
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
