from ariadne import (
    ObjectType,
    graphql_sync,
    load_schema_from_path,
    make_executable_schema,
    snake_case_fallback_resolvers,
)
from ariadne.constants import PLAYGROUND_HTML
from flask import Blueprint, jsonify, request

from crud.guild_crud import (
    resolve_create_guild,
    resolve_delete_guild,
    resolve_guild,
    resolve_guilds,
    resolve_update_guild,
)
from crud.member_crud import (
    resolve_create_member,
    resolve_delete_member,
    resolve_member,
    resolve_members,
    resolve_update_member,
)

bot = Blueprint("bot", __name__, url_prefix="/bot")
type_defs = load_schema_from_path("./schema.graphql")

query = ObjectType("Query")
query.set_field("members", resolve_members)
query.set_field("member", resolve_member)
query.set_field("guilds", resolve_guilds)
query.set_field("guild", resolve_guild)

mutation = ObjectType("Mutation")
mutation.set_field("createGuild", resolve_create_guild)
mutation.set_field("updateGuild", resolve_update_guild)
mutation.set_field("deleteGuild", resolve_delete_guild)
mutation.set_field("createMember", resolve_create_member)
mutation.set_field("updateMember", resolve_update_member)
mutation.set_field("deleteMember", resolve_delete_member)

schema = make_executable_schema(
    type_defs, query, mutation, snake_case_fallback_resolvers
)


@bot.route("/graphql/playground", methods=["GET"])
def playground():
    return PLAYGROUND_HTML, 200


@bot.route("/graphql", methods=["POST", "GET", "PATCH", "DELETE"])
def server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
    )

    status_code = result["data"][list(result["data"].keys())[0]]["code"]

    return jsonify(result["data"][list(result["data"].keys())[0]]), status_code
