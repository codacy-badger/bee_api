import os
basedir = os.path.abspath(os.path.dirname(__file__))
database_name = 'beehive.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, database_name)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    database_name = 'beehive_dev.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, database_name)

class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    database_name = 'beehive_test.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, database_name)
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
