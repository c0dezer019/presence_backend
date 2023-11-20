import pytest

from datetime import datetime
from fastapi.testclient import TestClient

from app.database.database import SessionLocal, test_engine
from app.database.models import Base, Guild, MemberShard
from main import app

Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


def test_table_creation(app):
    with app.app_context():
        assert sql.engine.dialect.has_table(sql.engine.connect(), "members")
        assert sql.engine.dialect.has_table(sql.engine.connect(), "guilds")


def test_create(app):
    guild1 = Guild(
        name="Taco Truck",
        guild_id=123456,
        last_activity="Texting",
        last_active_ts=datetime(2020, 12, 5, 11, 30, 5),
        last_active_channel="5674913213",
        date_added=datetime(2020, 4, 3, 2, 45),
    )  # type: ignore
    guild3 = Guild(
        name="Baristas Unite", guild_id=12344556, date_added=datetime(2021, 1, 1, 12, 0)
    )  # type: ignore
    user1 = Member(
        member_id=1,
        username="TestMember",
        discriminator=1234356789,
        date_added=datetime(2021, 3, 23, 5, 45, 12),
    )  # type: ignore
    user2 = Member(
        member_id=2,
        username="TestMember2",
        discriminator=12345,
        last_activity="Texting",
        last_active_server="1234567890",
        last_active_channel="5674913213",
        last_active_ts=datetime(2020, 12, 5, 11, 30, 5),
        date_added=datetime(2020, 4, 3, 2, 45),
    )  # type: ignore
    user3 = Member(
        member_id=3,
        username="TestMember3",
        discriminator=158239784,
        date_added=datetime(2021, 1, 1, 12, 0),
    )  # type: ignore

    guild1.members.append(user1)
    guild1.members.append(user2)
    guild3.members.append(user2)

    with app.app_context():
        sql.session.add(guild1)
        sql.session.add(guild3)
        sql.session.add(user1)
        sql.session.add(user2)
        sql.session.add(user3)
        sql.session.commit()
