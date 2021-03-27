from main import create_app
from datetime import datetime
from main.models import db
from main.config import TestConfiguration
from main.models import User, Server
import pytest


@pytest.fixture(scope = 'session')
def app():
    def _app(config_class):
        f_app = create_app(config_class)
        f_app.test_request_context().push()

        if config_class == 'main.config.TestConfiguration':
            db.drop_all()

        return f_app

    yield _app

    db.session.remove()

    if str(db.engine.url) == TestConfiguration.SQLALCHEMY_DATABASE_URI:
        db.drop_all()


@pytest.fixture(scope = 'module')
def create_servers():
    server1 = Server(name = 'Test Server', date_added = datetime(2021, 3, 23, 5, 13))
    server2 = Server(name = 'Taco Truck', last_activity = 'Texting',
                     last_activity_ts = datetime(2020, 12, 5, 11, 30, 5), date_added = datetime(2020, 4, 3, 2, 45))
    server3 = Server(date_added = datetime(2021, 1, 1, 12, 0))
    user1 = User(username = 'TestUser', date_added = datetime(2021, 3, 23, 5, 45, 12))
    user2 = User(username = 'TestUser2', last_activity = 'Texting', last_activity_loc = '#general',
                 last_activity_ts = datetime(2020, 12, 5, 11, 30, 5), date_added = datetime(2020, 4, 3, 2, 45))
    user3 = User(date_added = datetime(2021, 1, 1, 12, 0))

    server1.users.append(user1)
    server1.users.append(user2)
    server2.users.append(user3)
    server3.users.append(user2)
    user1.servers.append(server1)
    user2.servers.append(server1)
    user3.servers.append(server2)
    user2.servers.append(server3)

    db.session.add(server1)
    db.session.add(server2)
    db.session.add(server3)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()
