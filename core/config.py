from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def create_db_url(mode):
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


def create_session():
    engine = create_engine(
        create_db_url(getenv("MODE")), connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return SessionLocal


Base = declarative_base()
