from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool

from utils.types import Url

load_dotenv()


class Database:
    @staticmethod
    def _create_db_url(mode: str) -> Url:
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

        return Url(f"postgresql://{user}:{password}@{host}:{port}/{database}")

    def __init__(self):
        self.engine = create_engine(
            self._create_db_url(getenv("MODE")),
            echo=True if getenv("MODE") == "development" or getenv("MODE") == "testing" else False,
            poolclass=StaticPool if getenv("MODE") == "testing" else QueuePool
        )
        self.Session = sessionmaker(self.engine)
        self.session = self.Session()
