import pytest

from bee_api.app import app
from bee_api.database import db
from bee_api.classes.country.model import Country


@pytest.fixture(scope='module')
def test_client():
#    flask_app = create_app('flask_test.cfg')

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = app.test_client()

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    country1= Country(name='United States')
    country2 = Country(name='Canada')
#    user1 = User(email='patkennedy79@gmail.com', plaintext_password='FlaskIsAwesome')
#    user2 = User(email='kennedyfamilyrecipes@gmail.com', plaintext_password='PaSsWoRd')
    db.session.add(country1)
    db.session.add(country2)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()
