import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, create_engine
from bee_api.app import bcrypt, app, db
import jwt
from flask_security import UserMixin, RoleMixin

Base = declarative_base()

def create_tables(app):
    "Create tables, and return engine in case of further processing."
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    app.db.metadata.create_all(engine)
    return engine

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    api = db.Column(db.String(255))
    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    phoneNumber = db.Column(db.String(20))
    locationId = db.Column(db.Integer, ForeignKey('location.id'))
    location = db.relationship('Location', backref='user')
    registeredOn = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roleId = db.Column(db.Integer, ForeignKey('role.id'))
    role = db.relationship('Role', backref='user')
#    roles = db.relationship('Role', secondary=roles_users,
#                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return "{} {}".format(self.firstName, self.lastName)

#    @validates('email')
#    def validate_email(self, key, address):
#        assert '@' in address
#        return address

    def __init__(self, email, password, firstName = None, lastName = None,
                 phoneNumber = None,  locationId = None, roleId=None,
                 api=None):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.registeredOn = datetime.datetime.now()
        self.firstName = firstName
        self.lastName = lastName
        self.phoneNumber = phoneNumber
        self.locationId = locationId
        self.active = True
        self.roleId = roleId
        self.api = api
 #       if roles is None:
 #           roles = []
 #       self.roles = roles

    def encode_auth_token(self):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0,
                                seconds=app.config.get('SECRET_TIMEOUT')),
                'iat': datetime.datetime.utcnow(),
                'jti': self.id,
                'sub': self.id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                app.config.get('JWT_ALGORITHM')
            ).decode()
        except Exception as e:
            return e

#    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'),
                                 algorithms = app.config.get('JWT_ALGORITHM'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Country(db.Model):
    __tablename__ = 'country'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class StateProvince(db.Model):
    __tablename__ = 'stateProvince'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    countryId = db.Column(db.Integer, ForeignKey('country.id'))
    country = db.relationship('Country', backref='stateProvinces')
    name = db.Column(db.String(200))
    abbreviation = db.Column(db.String(10))

    def __repr__(self):
        return self.name


class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    streetAddress = db.Column(db.String(200))
    city = db.Column(db.String(200))
    stateProvinceId = db.Column(db.Integer, ForeignKey('stateProvince.id'))
    stateProvince = db.relationship('StateProvince', backref='location')


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


class Hive(db.Model):
    __tablename__ = "hive"
    id = db.Column(db.Integer, primary_key=True)
    ownerId = db.Column(db.Integer, ForeignKey('user.id'))
    owner = db.relationship('User', backref='hives')
# Hive location may differ from the location of the bee keeper
    locationId = db.Column(db.Integer, ForeignKey('location.id'))
    location = db.relationship('Location', backref='hives')
    dateCreated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    lastUpdate = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#    door_open = Column(Boolean, server_default=True)


class HiveData(db.Model):
    __tablename__ = "hiveData"
    id = db.Column(db.Integer, primary_key=True)
    hiveId = db.Column(db.Integer, ForeignKey('hive.id'))
    hive = db.relationship('Hive', backref='hiveData')
    dateCreated = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    temperature = db.Column(db.Numeric)
    humidity = db.Column(db.Numeric)
    sensor = db.Column(db.Integer)
    outdoor = db.Column(db.BOOLEAN)
