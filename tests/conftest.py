# Third party modules
import pytest

# Internal modules
from main import app


@pytest.fixture(scope="session")
def fastapi():
    fastapi = app()

    yield fastapi


def test_app(fastapi):
    # Third party modules
    from fastapi import FastAPI

    assert type(app) is FastAPI
