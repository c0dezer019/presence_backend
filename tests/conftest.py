from app import create_app
import pytest


@pytest.fixture
def client():
    flask_app = create_app('config.TestConfiguration')

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            flask_app.init_db()
        yield client
