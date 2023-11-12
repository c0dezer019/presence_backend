from ariadne import (
    MutationType,
    QueryType,
    graphql_sync,
    load_schema_from_path,
    make_executable_schema,
)
from ariadne.explorer import ExplorerGraphiQL

from flask import Blueprint, jsonify, request

from ..crud.guild_crud import (
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

bot = Blueprint("bot", __name__, url_prefix="/bot")
schema = make_executable_schema(
    type_defs, query, mutation, convert_names_case=True
)
explorer_html = ExplorerGraphiQL().html(None)

@bot.route("/graphql/explore", methods=["GET", "POST"])
def explore():
    return explorer_html, 200


@bot.route("/graphql", methods=["POST"])
def server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
    )

    status_code = 200 if success else 400

    return jsonify(result), status_code
