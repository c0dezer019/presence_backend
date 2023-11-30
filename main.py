# Third part modules
from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

# Internal modules
from app.database import LocalSession
from app.database.models import Base
from app.graphql import query, mutation


Base.metadata.create_all(LocalSession.engine)


def get_db():
    db = LocalSession.session
    try:
        yield db
    finally:
        db.close()


def graphql_app():
    app_schema = strawberry.Schema(query=query, mutation=mutation)
    graphql_app = GraphQLRouter(app_schema)

    return graphql_app


def app():
    fastapi = FastAPI(name=__name__)
    fastapi.include_router(graphql_app(), prefix="/graphql")

    return fastapi
