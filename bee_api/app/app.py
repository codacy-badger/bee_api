import decimal
from dateutil import parser
import flask.json

from flask import Flask, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_restless import ProcessingException
from flask_security import auth_token_required, SQLAlchemyUserDatastore, \
        Security
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, \
    get_jwt_identity, get_jwt_claims
from bee_api.app import db, app, bcrypt
from bee_api.schema import *
from bee_api.models import User, Country, Location, Hive, HiveData,\
    StateProvince, BlacklistToken, Role


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

country_schema = CountrySchema()
countries_schema = CountrySchema(many=True)
stateProvince_schema = StateProvinceSchema()
stateProvinces_schema = StateProvinceSchema(many=True)
location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
hive_schema = HiveSchema()
hives_schema = HiveSchema(many=True)
hiveData_schema = HiveDataSchema()
hiveDatas_schema = HiveDataSchema(many=True)


class DecJSONEncoder(flask.json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return str(obj)
        return super(DecJSONEncoder, self).default(obj)


jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_access_token(user):
    if user.roleId is None:
        role_name = None
    else:
        role = Role.query.get(user.roleId)
        role_name = role.name

    return {'roles': role_name}

#@jwt.user_loader_callback_loader
#def user_loader_callback(identity):
#    user = User.query.get(identity)
#    if user is None:
#        return None

#    if user.roleId is None:
#        role_name = None
#    else:
#        role = Role.query.get(user.roleId)
#        role_name = role.name
#    return dict(id=identity, roles=role_name)
#    return user

@jwt.user_identity_loader
def get_identity_for_access_token(user):
    return user.id


def add_country_helper(json_data):
    country = Country(name=json_data['name'],)
    db.session.add(country)
    db.session.commit()
    return country

def add_user_helper(json_data):
    if 'firstName' in json_data:
        fname = json_data.get('firstName')
    else:
        fname = None
    if 'lastName' in json_data:
        lname = json_data.get('lastName')
    else:
        lname = None
    if 'phoneNumber' in json_data:
        phonenumber = json_data.get('phoneNumber')
    else:
        phonenumber = None
    if 'locationId' in json_data:
        location = json_data.get('locationId')
    else:
        location = None
    if 'roles' in json_data:
        role = Role.query.filter_by(name=json_data['roles']).first()
        role_id = role.id
    else:
        role_id = None

    try:
        user = User(
            email=json_data.get('email'),
            password=json_data.get('password'),
            firstName=fname,
            lastName=lname,
            phoneNumber=phonenumber,
            locationId=location,
            roleId=role_id
        )
        db.session.add(user)
        db.session.commit()
        # generate the auth token
        auth_token = user.encode_auth_token()
        responseObject = {
            'status': 'success',
            'message': 'Successfully registered.',
            'auth_token': auth_token
        }
        return jsonify(responseObject), 201
    except Exception as e:
        responseObject = {
            'status': 'fail',
            'message': 'Some error occurred. Please try again.'
        }
        return jsonify(responseObject), 401


@app.route('/countries')
def get_countries():
    results = Country.query.all()
    result = countries_schema.dump(results)
    return jsonify({'countries': result.data})


@app.route("/countries/<int:pk>")
def get_country(pk):
    try:
        country = Country.query.get(pk)
    except IntegrityError:
        return jsonify({"message": "Country could not be found."}), 400
    result = country_schema.dump(country)
    return jsonify({"countries": result.data})


@app.route("/countries", methods=["POST"])
@jwt_required
def new_country():
    current_user = get_jwt_claims()

    if 'admin' not in current_user['roles']:
        return jsonify({'message': 'Forbidden'}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    data, errors = country_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    if Country.query.filter_by(name=data['name']).first():
        raise ProcessingException(
            description='State, {}, already exists'.format(
                data['name']), code=409)
        return

    country = add_country_helper(data)
    result = country_schema.dump(Country.query.get(country.id))
    return jsonify({"message": "Created new Country.",
                    "Country": result.data})


@app.route('/state-provinces')
def get_stateProvinces():
    stateprovinces = StateProvince.query.all()
    # Serialize the queryset
    result = stateProvinces_schema.dump(stateprovinces)
    return jsonify({'stateprovinces': result.data})


@app.route("/state-provinces/<int:pk>")
def get_stateProvince(pk):
    try:
        stateProvince = StateProvince.query.get(pk)
    except IntegrityError:
        return jsonify({"message": "State/Province could not be found."}), 400
    result = stateProvince_schema.dump(stateProvince)
    return jsonify({"stateprovinces": result.data})


@app.route("/state-provinces", methods=["POST"])
@jwt_required
def new_stateprovinces():
    current_user = get_jwt_claims()

    if 'admin' not in current_user['roles']:
        return jsonify({'message': 'Forbidden'}), 403

    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    data, errors = stateProvince_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    country = Country.query.filter_by(
        name=json_data['country']['name']).first()
    if country is None:
        country = Country(name=json_data['country']['name'])
        db.session.add(country)

    if StateProvince.query.filter_by(
        name=json_data['name'],
        abbreviation=json_data['abbreviation']).first():
            raise ProcessingException(
                description='State, {}, already exists'.format(
                    json_data['name']), code=409)
            return

    stateProvince = StateProvince(
        name = json_data['name'],
        abbreviation = json_data['abbreviation'],
        countryId = country.id
#        country = country
    )
    db.session.add(stateProvince)
    db.session.commit()
    result = StateProvince.query.get(stateProvince.id)
    result = stateProvince_schema.dump(StateProvince.query.get(stateProvince.id))
    return jsonify({"message": "Created new State/Province.",
                    "stateprovinces": result.data})


@app.route('/locations')
@jwt_required
def get_locations():
    current_user = get_jwt_claims()

    if 'admin' not in current_user['roles']:
        return jsonify({'message': 'Forbidden'}), 403

    locations = Location.query.all()
    result = locations_schema.dump(locations)
    return jsonify({'locations': result.data})


@app.route("/locations/<int:pk>")
def get_location(pk):
    current_user = get_jwt_claims()

#    if 'admin' not in current_user['roles']:
#        return jsonify({'message': 'Forbidden'}), 403

    try:
        location = Location.query.get(pk)
    except IntegrityError:
        return jsonify({"message": "Location could not be found."}), 400
    result = location_schema.dump(location)
    return jsonify({"locations": result.data})


@app.route("/locations", methods=["POST"])
def new_locations():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    data, errors = location_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    stateProv = StateProvince.query.filter_by(
        id = data['stateProvince']['id']
    )

    if stateProv is None:
        country = Country.query.filter_by(
            name=data['stateprovince']['country']['name']
        )
        if country is None:
            country = Country(
                name=data['stateProvince']['country']['name'])
            db.session.add(country)
            stateProv = StateProvince(
               name=data['stateprovince']['name'],
               abbreviation = data['stateprovince']['abbreviation'],
               country = country
        )

    if Location.query.filter_by(
        streetAddress=data['streetAddress'],
        city=data['city'],
        stateProvinceId=data['stateProvince']['id']).first():
        raise ProcessingException(
            description='Location, {}, {}, already exists'.format(
                data['streetAddress'], data['city']), code=409)
        return

    location = Location(
        streetAddress=data['streetAddress'],
        city=data['city'],
        stateProvinceId=data['stateProvince']['id'])

    db.session.add(location)
    db.session.commit()
    result = location_schema.dump(location.query.get(location.id))
    return jsonify({"message": "Created new Location.",
                    "locations": result.data})


@app.route('/users')
@jwt_required
def get_owners():
    current_user = get_jwt_claims()

    if 'admin' not in current_user['roles']:
        return jsonify({'message': 'Forbidden'}), 403

    results = User.query.all()
    result = users_schema.dump(results)
    return jsonify({'users': result.data})


@app.route("/users/<int:pk>")
@jwt_required
def get_user(pk):
    current_claim = get_jwt_claims()
    current_user = get_jwt_identity()
    if 'admin' not in current_claim['roles'] and \
        current_user != pk:
        return jsonify({'message': 'Forbidden'}), 403

    try:
        results = User.query.get(pk)
    except IntegrityError:
        return jsonify({"message": "User could not be found."}), 400

    if results is None:
        return jsonify({"message": "User could not be found."}), 400

    result = user_schema.dump(results)
    return jsonify({"users": result.data})


@app.route("/auth/register", methods=["POST"])
def new_registration():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    data, errors = user_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    user = User.query.filter_by(email=data.get('email')).first()
    if not user:
        return add_user_helper(json_data)
    else:
        responseObject = {
            'status': 'fail',
            'message': 'User already exists. Please Log in.',
        }
        return jsonify(responseObject), 202


@app.route("/auth/login", methods=["POST"])
def login():
    # get the post data
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    data, errors = user_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    try:
        # fetch the user data
        user = User.query.filter_by(email=json_data.get('email')).first()
        if user and bcrypt.check_password_hash(user.password,
                                        json_data.get('password')):
            access_token = create_access_token(identity=user)
#            access_token = create_access_token(identity=user)
            if access_token:
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': access_token
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User does not exist.'
            }
            return jsonify(responseObject), 404
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail',
            'message': 'Try again'
        }
        return jsonify(responseObject), 500

@app.route("/auth/api", methods=["POST"])
def api_login():
    # get the post data
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
    # Validate and deserialize input
    data, errors = user_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    try:
        # fetch the user data
        user = User.query.filter_by(api=json_data.get('api')).first()
        if user:
            access_token = create_access_token(identity=user)
#            access_token = create_access_token(identity=user)
            if access_token:
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged in.',
                    'auth_token': access_token
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': 'User does not exist.'
            }
            return jsonify(responseObject), 404
    except Exception as e:
        print(e)
        responseObject = {
            'status': 'fail',
            'message': 'Try again'
        }
        return jsonify(responseObject), 500


@app.route("/auth/logout", methods=["POST"])
@auth_token_required
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ''
    if auth_token:
        resp = User.decode_auth_token(auth_token)
        if not isinstance(resp, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                db.session.add(blacklist_token)
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'message': 'Successfully logged out.'
                }
                return jsonify(responseObject), 200
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': e
                }
                return jsonify(responseObject), 200
        else:
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return jsonify(responseObject), 401
    else:
        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return jsonify(responseObject), 403


@app.route('/hives')
@jwt_required
def get_hives():
    results = Hive.query.all()
    result = hives_schema.dump(results)
    return jsonify({'hives': result.data})


@app.route("/hives/<int:pk>")
@jwt_required
def get_hive(pk):
    try:
        results = Hive.query.get(pk)
    except IntegrityError:
        return jsonify({"message": "Hive could not be found."}), 400
    result = hive_schema.dump(results)
    return jsonify({"hives": result.data})


@app.route("/hivedata/", methods=["POST"])
@jwt_required
def new_hivedata():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'message': 'No input data provided'}), 400
        # Validate and deserialize input
    data, errors = hiveData_schema.load(json_data)
    if errors:
        return jsonify(errors), 422

    hiveId = Hive.query.filter_by(
            id=data['hive']['id']
        )

    if hiveId is None:
        return jsonify({'message': 'Invalid Hive Id'}), 400

    try:
        for probe in data['probes']:
            hiveData = HiveData(hiveId = data['hive']['id'],
                                temperature = probe['temperature'],
                                humidity = probe['humidity'],
                                sensor = probe['sensor'],
                                outdoor = probe['outdoor'],
                                dateCreated = parser.parse(
                                    data['dateCreated']))
            db.session.add(hiveData)
    except KeyError as k:
        return jsonify({'message': 'Invalid key: {}'.format(k)}), 406

    db.session.commit()
    return jsonify({"message": "Updated Hive Data"})


@app.route("/hivedata/<int:pk>")
@jwt_required
def get_hivedata_id(pk):
    try:
        results = HiveData.query.get(pk)
    except IntegrityError:
        return jsonify({"message": "Hive Data could not be found."}), 400
    result = hiveData_schema.dump(results)
    return jsonify({"hivedata": result.data})


@app.route("/hivedata")
@jwt_required
def get_hivedata():
    try:
        results = HiveData.query.all()
    except IntegrityError:
        return jsonify({"message": "Hive Data could not be found."}), 400
    result = hiveDatas_schema.dump(results)
    return jsonify({"hivedata": result.data})


@app.route("/")
@jwt_required
def get_index():
    return jsonify({"message": "hello"})


if __name__ == '__main__':
   app.run(host='0.0.0.0')