import pytest

from core import create_app


@pytest.fixture(scope="session")
def app():
    '''Sets up an instance'''
    app = create_app("TestConfig")

    yield app


def test_app(app):
    from flask.app import Flask

    assert type(app) == Flask
