import logging
from logging.handlers import RotatingFileHandler

# Third part modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter

# Internal modules
from app.database import database, engine
from app.database.models import Base
from app.graphql.schema import Query, Mutation

Base.metadata.create_all(engine)

origins = [
    "http://localhost:8000",
    "https://localhost:8000",
    "http://127.0.0.1:5432"
]


def get_db():
    db = database.database()
    try:
        yield db
    finally:
        db.close()


def graphql_app():
    app_schema = Schema(query=Query, mutation=Mutation)
    gql_app = GraphQLRouter(app_schema)

    return gql_app


def app():
    fastapi = FastAPI(name=__name__)
    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    fastapi.include_router(graphql_app(), prefix="/gql")

    return fastapi


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("server_log.txt", max_Bytes=500000, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
