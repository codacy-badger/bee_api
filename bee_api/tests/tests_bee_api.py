import os
import glob
import json
from flask_fixtures import load_fixtures
from flask_fixtures.loaders import JSONLoader
from bee_api.api.api import db, app
from datetime import datetime

import unittest


class BeeWebTestCase(unittest.TestCase):
    def create_app(self):
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

        return app

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
        with app.app_context():
            db.drop_all()
#            os.close(self.db_fd)
#            os.unlink(app.config['DATABASE'])


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

    def test_add_country(self):
        rv = self.app.post('/countries/',
                           content_type='application/json',
                           data=json.dumps(dict(name='West Germany')))

        self.assertEqual(rv.status_code, 200)

        rv = self.app.post('/countries/',
                           content_type='application/json',
                           data=json.dumps({'name':'West Germany'}))

        self.assertEqual(rv.status_code, 409)


    def test_get_all_statesprovinces(self):
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

    def test_add_stateprovinces(self):
        json_data = dict(name="Quebec", abbreviation="QC",
                     country=dict(name="Canada", id=2))
        rv = self.app.post('/state-provinces/',
                           data = json.dumps(json_data),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['stateprovinces']['abbreviation'], 'QC')
        self.assertEqual(json_resp['stateprovinces']['name'], 'Quebec')
        self.assertEqual(json_resp['stateprovinces']['country']['id'], 2)

        json_data = dict(name="Quebec", abbreviation="QC",
                     country=dict(name="Canada", id=2))

        rv = self.app.post('/state-provinces/',
                           data = json.dumps(json_data),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 409)

    def test_add_location(self):
        rv = self.app.post('/locations/',
                           content_type='application/json',
                           data=json.dumps(dict(city='Hanover',
                                streetAddress='84 Summer St.',
                                stateProvince=dict(name='Massachusetts', id=21))))

        self.assertEqual(rv.status_code, 200)

    def test_get_all_locations(self):
        rv = self.app.get('/locations')
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


    def test_get_owners(self):
        rv = self.app.get('/owners/1')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['owners']['firstName'], 'Mickey')
        self.assertEqual(json_resp['owners']['lastName'], 'Mouse')
        self.assertEqual(json_resp['owners']['email'], 'mm@disney.com')
        self.assertEqual(json_resp['owners']['location']['city'], 'Boston')
        self.assertEqual(json_resp['owners']['location']['id'], 1)
        self.assertEqual(json_resp['owners']['location']['streetAddress'],
                         '123 Main St.')
        self.assertEqual(json_resp['owners']['phoneNumber'],
                         '7812175265')


    def test_add_hivedata(self):
        json_data = dict(probes=[
                            dict(humidity = 10.5, temperature = 78.5,
                            outdoor = False, sensor = 11),
                            dict(humidity=20.5, temperature=88.5,
                            outdoor=True, sensor=22)
                            ], hive=dict(id=1),
                            dateCreated=datetime.utcnow().__str__())
        rv = self.app.post('/hivedata/',
                           data = json.dumps(json_data),
                           content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        json_resp = json.loads(rv.data)
        self.assertEqual(json_resp['message'], 'Updated Hive Data')


if __name__ == '__main__':
    unittest.main()