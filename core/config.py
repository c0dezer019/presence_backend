from dotenv import load_dotenv
from os import getenv

load_dotenv()

def create_db_url(mode):
    db = getenv('DB')
    user = getenv('USER')
    password = getenv('PASSWORD')
    host = getenv('HOST')
    port = getenv('PORT')

    if mode == 'testing':
        db = getenv('T_DB')

    elif mode == 'production':
        db = getenv('CP_DB')
        user = getenv('CP_USER')
        password = getenv('CP_PASSWORD')
        host = getenv('CP_HOST')

    return f'postgresql://{user}:{password}@{host}:{port}/{db}'


class BaseConfig(object):
    TESTING = False


class DevConfig(BaseConfig):
    DEBUG = False
    MODE = 'development'
    SECRET = getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = create_db_url('development')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    HASH_ROUNDS = 100000


class TestConfig(BaseConfig):
    DEBUG = True
    MODE = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = create_db_url('testing')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_ENABLED = False
    HASH_ROUNDS = 1


class ProductionConfig(BaseConfig):
    MODE = 'production'
    SQLALCHEMY_DATABASE_URI = create_db_url('production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
