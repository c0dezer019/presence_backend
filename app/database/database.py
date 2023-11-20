from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


engine = create_engine(
    create_db_url("development" if getenv("MODE") == "development" else "production")
)
test_engine = create_engine(create_db_url("testing"), poolclass=StaticPool)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
