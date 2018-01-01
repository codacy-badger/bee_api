import os

class BaseConfig:
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_name = 'beehive.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, database_name)
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    SECRET_TIMEOUT = int(os.getenv('SECRET_TIMEOUT', '900'))
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    JWT_IDENTITY_CLAIM = os.getenv('ID_CLAIM', 'sub')


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    database_name = 'beehive_dev.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BaseConfig.basedir,
                                                          database_name)


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    database_name = 'beehive_test.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BaseConfig.basedir,
                                                          database_name)

    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    SECRET_KEY = 'my_precious_production'
    DEBUG = False
