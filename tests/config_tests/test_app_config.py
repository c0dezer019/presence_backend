'''Test that config is correctly setup.'''

import pytest

from flask.app import Flask

from core import create_app
from core.config import DevConfig, TestConfig, create_db_url

@pytest.fixture
def dev_app():
    return create_app()


@pytest.fixture
def t_app():
    return create_app("TestConfig")


def test_dev_app(dev_app):
    '''App is created with development configuration and configured correctly.'''

    assert type(dev_app) == Flask
    assert DevConfig.SQLALCHEMY_DATABASE_URI == create_db_url("development")
    assert dev_app.config["DEBUG"] is True
    assert dev_app.config["TESTING"] is False
    assert dev_app.config["SQLALCHEMY_ECHO"] is True
    assert dev_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is True
    assert dev_app.config["SQLALCHEMY_DATABASE_URI"] == DevConfig.SQLALCHEMY_DATABASE_URI

def test_test_app(t_app):
    '''App is created with test configuration and configured correctly'''

    assert type(t_app) == Flask
    assert TestConfig.SQLALCHEMY_DATABASE_URI == create_db_url("testing")
    assert t_app.config["DEBUG"] is True
    assert t_app.config["TESTING"] is True
    assert t_app.config["SQLALCHEMY_ECHO"] is True
    assert t_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is True
    assert t_app.config["SQLALCHEMY_DATABASE_URI"] == TestConfig.SQLALCHEMY_DATABASE_URI
