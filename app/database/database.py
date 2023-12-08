from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv()


def _create_db_url(mode):
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
        database = getenv("PROD_DB")
        user = getenv("PROD_USER")
        password = getenv("PROD_PASSWORD")
        host = getenv("PROD_HOST")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


class LocalSession:

    def __init__(self):
        self.engine = create_engine(
            _create_db_url(
                "development" if getenv("MODE") == "development" else "production"
            ),
            echo=True,
        )
        self.Session = sessionmaker(self.engine)


class TestSession(LocalSession):
    def __init__(self):
        super().__init__()
        self.engine = create_engine(
            _create_db_url("testing"), poolclass=StaticPool
        )


class Base(DeclarativeBase):
    pass
