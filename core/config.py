from os import getenv

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base

load_dotenv()

sql = SQLAlchemy(model_class=declarative_base())


def create_db_url(mode):
    database = getenv("DEV_DB")
    user = getenv("DEV_USER")
    password = getenv("DEV_PASSWORD")
    host = getenv("HOST")
    port = getenv("PORT")

    if mode == "testing":
        database = getenv("TEST_DB")
        user = getenv("TEST_USER")
        password = getenv("TEST_PASSWORD")

    elif mode == "production":
        database = getenv("CP_DB")
        user = getenv("CP_USER")
        password = getenv("CP_PASSWORD")
        host = getenv("CP_HOST")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


class BaseConfig(object):
    TESTING = False


class DevConfig(BaseConfig):
    DEBUG = False
    MODE = "development"
    SECRET = getenv("SECRET")
    SQLALCHEMY_DATABASE_URI = create_db_url("development")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    HASH_ROUNDS = 100000


class TestConfig(BaseConfig):
    DEBUG = True
    MODE = "testing"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = create_db_url("testing")
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = True
    WTF_CSRF_ENABLED = False
    HASH_ROUNDS = 1


class ProductionConfig(BaseConfig):
    MODE = "production"
    SQLALCHEMY_DATABASE_URI = create_db_url("production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
