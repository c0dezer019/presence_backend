from dotenv import load_dotenv
from pathlib import Path
from os import getenv

env_path = Path('', '../.env')
load_dotenv(dotenv_path = env_path)


def create_db_url(mode):
    db = getenv('DB')
    user = getenv('USER')
    password = getenv('PASS')
    host = getenv('HOST')
    port = getenv('PORT')

    if mode == 'development':
        db = getenv('DB')

    elif mode == 'testing':
        db = getenv('T_DB')

    elif mode == 'production':
        db = getenv('CP_DB')
        user = getenv('CP_USER')
        password = getenv('CP_PASS')
        host = getenv('CP_HOST')

    return f'postgresql://{user}:{password}@{host}:{port}/{db}'


class BaseConfiguration(object):
    DEBUG = False
    MODE = 'development'
    TESTING = False
    SECRET = getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = create_db_url('development')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    HASH_ROUNDS = 100000


class TestConfiguration(BaseConfiguration):
    DEBUG = True
    MODE = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = create_db_url('testing')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WTF_CSRF_ENABLED = False
    HASH_ROUNDS = 1


class ProductionConfiguration(BaseConfiguration):
    MODE = 'production'
    SQLALCHEMY_DATABASE_URI = create_db_url('production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
