import json
from gql import gql

from tests.support.assertions import assert_valid_schema


def test_home_page(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    json_data = json.loads(response.data.decode('utf-8'))
    assert_valid_schema(json_data, 'home.json')


def test_country_list(test_client):
    query = gql('''
         query CountryQuery {
             countryList {
             edges {
             node {
                 name
             }
         }
         }
     }
    ''')
    response = test_client.post('/graphql')
