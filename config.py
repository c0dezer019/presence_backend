from dotenv import load_dotenv
from pathlib import Path
from os import getenv

env_path = Path('.', '.env')
load_dotenv(dotenv_path = env_path)

# Database configs
development = dict(
    DB = getenv('DB'),
    USER = getenv('USER'),
    PASS = getenv('PASS'),
    HOST = getenv('HOST'),
    PORT = getenv('PORT'),
)
testing = dict(
    DB = getenv('T_DB'),
    USER = getenv('USER'),
    PASS = getenv('PASS'),
    HOST = getenv('HOST'),
    PORT = getenv('PORT'),
)
production = dict(
    DB = getenv('CP_DB'),
    USER = getenv('CP_USER'),
    PASS = getenv('CP_PASS'),
    HOST = getenv('CP_HOST'),
    PORT = getenv('PORT'),
)

# Packaging config dicts for easier switching
env = {
    'development': development,
    'testing': testing,
    'production': production
}
MODE = 'development'
env = env[MODE]

USER = env['USER']
PASS = env['PASS']
HOST = env['HOST']
PORT = env['PORT']
DB = env['DB']

URI_STRING = f'{USER}:{PASS}@{HOST}:{PORT}/{DB}'


class BaseConfiguration(object):
    DEBUG = False
    MODE = 'development'

    SECRET = getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{URI_STRING}'
    SQLALCHEMY_ECHO = True
    HASH_ROUNDS = 100000


class TestConfiguration(BaseConfiguration):
    MODE = 'testing'
    SQLALCHEMY_DATABASE_URI = f'postgresql://:memory:{URI_STRING}'
    WTF_CSRF_ENABLED = False
    HASH_ROUNDS = 1


class ProductionConfiguration(BaseConfiguration):
    MODE = 'production'
