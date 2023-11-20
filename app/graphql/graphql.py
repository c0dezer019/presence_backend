from ariadne import (
    MutationType,
    QueryType,
    load_schema_from_path,
    make_executable_schema,
)
from ariadne.asgi import GraphQL
from ariadne.asgi.handlers import GraphQLTransportWSHandler
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute

from ..crud.guild import (
    resolve_create_guild,
    resolve_delete_guild,
    resolve_guild,
    resolve_guilds,
    resolve_update_guild,
)
from ..crud.member_crud import (
    resolve_create_member,
    resolve_delete_member,
    resolve_member,
    resolve_members,
    resolve_update_member,
)

type_defs = load_schema_from_path("core/graphql/schema.graphql")

query = QueryType()
query.set_field("members", resolve_members)
query.set_field("member", resolve_member)
query.set_field("guilds", resolve_guilds)
query.set_field("guild", resolve_guild)

mutation = MutationType()
mutation.set_field("createGuild", resolve_create_guild)
mutation.set_field("updateGuild", resolve_update_guild)
mutation.set_field("deleteGuild", resolve_delete_guild)
mutation.set_field("createMember", resolve_create_member)
mutation.set_field("updateMember", resolve_update_member)
mutation.set_field("deleteMember", resolve_delete_member)

schema = make_executable_schema(
    type_defs, query, mutation, convert_names_case=True
)

graphql_app = GraphQL(
    schema,
    debug=True,
    websocket_handler=GraphQLTransportWSHandler(),
)

app = Starlette(
    routes=[
        Route("/graphql/", graphql_app.handle_request, methods=["GET", "POST", "OPTIONS"]),
        WebSocketRoute("/graphql", graphql_app.handle_websocket)
    ]
)