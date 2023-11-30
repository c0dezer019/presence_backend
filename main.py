# Third part modules
from fastapi import FastAPI

# Internal modules
from app.database import LocalSession
from app.database.models import Base


Base.metadata.create_all(LocalSession.engine)

def get_db():
    db = LocalSession.session
    try:
        yield db
    finally:
        db.close()

def app():
    fastapi = FastAPI(name=__name__)

    return fastapi
