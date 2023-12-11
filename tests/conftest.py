import pytest

from main import app


@pytest.fixture(scope="session")
def fastapi():
    fastapi = app()

    yield fastapi


def test_app(fastapi):
    from fastapi import FastAPI

    assert type(app) is FastAPI
