from core import create_app
from datetime import datetime
from core.models import db
from core.config import TestConfiguration
from core.models import Member, Guild
import pytest


@pytest.fixture(scope = 'session')
def app():
    def _app(config_class):
        f_app = create_app(config_class)
        f_app.test_request_context().push()

        if config_class == 'core.config.TestConfiguration':
            db.drop_all()

        return f_app

    yield _app

    db.session.remove()

    if str(db.engine.url) == TestConfiguration.SQLALCHEMY_DATABASE_URI:
        db.drop_all()


@pytest.fixture(scope = 'module')
def create_guilds():
    guild1 = Guild(name = 'Test Guild', date_added = datetime(2021, 3, 23, 5, 13))
    guild2 = Guild(name = 'Taco Truck',
                   last_activity = 'Texting',
                   last_active_ts = datetime(2020, 12, 5, 11, 30, 5),
                   last_active_channel = '5674913213',
                   date_added = datetime(2020, 4, 3, 2, 45))
    guild3 = Guild(date_added = datetime(2021, 1, 1, 12, 0))
    user1 = Member(username = 'TestMember', date_added = datetime(2021, 3, 23, 5, 45, 12))
    user2 = Member(username = 'TestMember2',
                   last_activity = 'Texting',
                   last_active_server = '1234567890',
                   last_active_channel = '5674913213',
                   last_active_ts = datetime(2020, 12, 5, 11, 30, 5),
                   date_added = datetime(2020, 4, 3, 2, 45))
    user3 = Member(date_added = datetime(2021, 1, 1, 12, 0))

    guild1.members.append(user1)
    guild1.members.append(user2)
    guild2.members.append(user3)
    guild3.members.append(user2)
    user1.guilds.append(guild1)
    user2.guilds.append(guild1)
    user3.guilds.append(guild2)
    user2.guilds.append(guild3)

    db.session.add(guild1)
    db.session.add(guild2)
    db.session.add(guild3)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()
