import pytest
import json
from graphql.error import format_error
from gql import Client, gql
from bee_api.classes.country.schema import Country
from bee_api.tests.support.assertions import assert_valid_schema


@pytest.fixture
def client():
    return Client(schema=Country)


def test_country_name_query(client):
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
    response = client.execute(query)
    assert response.status_code == 200
    json_data = json.loads(response.data.decode('utf-8'))
    assert_valid_schema(json_data, 'country_query_graphql.json')
