# Third part modules
# Third party modules
from fastapi import FastAPI
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter

# Internal modules
from app.database import db, engine
from app.database.models import BaseModel
from app.graphql.schema import Mutation, Query
from app.utils.logging import Logger, rel

BaseModel.metadata.create_all(engine)

logger = Logger(rel(__file__), __name__).logger()


def get_db():
    _db = db.session
    try:
        yield _db
    finally:
        _db.close()


def graphql_app():
    app_schema = Schema(query=Query, mutation=Mutation)
    gql_app = GraphQLRouter(app_schema)

    return gql_app


def app():
    fastapi = FastAPI(name=__name__)

    fastapi.include_router(graphql_app(), prefix="/gql")
    return fastapi


_app = app()
