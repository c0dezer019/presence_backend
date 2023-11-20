import pytest

from main import app


@pytest.fixture(scope="session")
def fastapi():
    '''Sets up an instance'''
    fastapi = app()

    yield fastapi


def test_app(app):
    from fastapi import FastAPI

    assert type(app) == FastAPI
