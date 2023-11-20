# Third part modules
from fastapi import FastAPI

# Internal modules
from app.database import SessionLocal, engine, models


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def app():
    models.Base.metadata.create_all(bind=engine)
    fastapi = FastAPI(name=__name__)

    return fastapi
