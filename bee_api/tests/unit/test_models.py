import pytest
from classes.country.model import Country
from classes.state_province.model import StateProvince
from classes.location.model import Location
from classes.user.model import (User, Role)
from classes.hive.model import (HiveData, Hive)


@pytest.fixture(scope='module')
def new_country():
    return Country(name='Great Britain')


@pytest.fixture(scope='module')
@pytest.mark.usefixtures('new_country')
def new_state_province(new_country):
    return StateProvince(country=new_country, name='Mickey State',
                         abbreviation='MS')


@pytest.fixture(scope='module')
@pytest.mark.usefixtures('new_state_province')
def new_location(new_state_province):
    return Location(street_address='123 Main St.', city='Somewhere',
                        postal_code='01234',
                        state_province=new_state_province)


@pytest.fixture(scope='module')
def new_role():
    role_list = []
    role_list.append(Role(name='queen', description='Queen bee'))
    return role_list


#@pytest.fixture(scope='module')
#@pytest.mark.usefixtures('new_user', 'new_role')
#def new_user_role(new_user, new_role):
#    return RolesUsers(role_id=new_role.id, user_id=new_user.id)


@pytest.fixture(scope='module')
@pytest.mark.usefixtures('new_location', 'new_role')
def new_user(new_location, new_role):
    return User(email='bee.mine@bee.org', password='password',
                firstName='Queen', lastName='Bee', phoneNumber='1234567890',
                location=new_location, roles=new_role)


@pytest.fixture(scope='module')
@pytest.mark.usefixtures('new_location', 'new_user')
def new_hive(new_location, new_user):
    return Hive(location=new_location, owner=new_user)


@pytest.mark.usefixtures('new_role')
def test_new_role(new_role):
    assert new_role[0].name == 'queen'
    assert new_role[0].description == 'Queen bee'


@pytest.mark.usefixtures('new_user', 'new_role', 'new_location')
def test_new_user(new_user, new_role, new_location):
    assert new_user.firstName == 'Queen'
    assert new_user.lastName == 'Bee'
    assert new_user.email == 'bee.mine@bee.org'
    assert new_user.password == 'password'
    assert new_user.phoneNumber == '1234567890'
    assert new_user.location == new_location
    assert new_user.roles == new_role


def test_new_country(new_country):
    assert new_country.name == 'Great Britain'


@pytest.mark.usefixtures('new_location', 'new_state_province')
def test_new_location(new_location, new_state_province):
    assert new_location.state_province == new_state_province
    assert new_location.street_address == '123 Main St.'
    assert new_location.city == 'Somewhere'
    assert new_location.postal_code == '01234'


@pytest.mark.usefixtures('new_hive', 'new_user', 'new_location')
def test_new_hive(new_hive, new_user, new_location):
    assert new_hive.location == new_location
    assert new_hive.owner == new_user


@pytest.mark.usefixtures('new_hive')
def test_new_hive_data(new_hive):
    hive_data = HiveData(hive=new_hive, temperature=90.0, humidity=50.4,
                         sensor=1, outdoor=False)
    assert hive_data.hive == new_hive
    assert hive_data.humidity == 50.4
    assert hive_data.temperature == 90.0
    assert hive_data.sensor == 1
    assert hive_data.outdoor is False

    hive_data = HiveData(hive=new_hive, temperature=80.0, humidity=40.4,
                         sensor=2, outdoor=True)
    assert hive_data.hive == new_hive
    assert hive_data.humidity == 40.4
    assert hive_data.temperature == 80.0
    assert hive_data.sensor == 2
    assert hive_data.outdoor is True
