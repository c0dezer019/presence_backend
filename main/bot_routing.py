from flask import Blueprint, jsonify, request
from crud.member_crud import add_member, get_member, get_all_members, update_member, remove_member
from crud.guild_crud import add_guild, get_guild, get_all_guilds, update_guild, remove_guild


bot = Blueprint('bot', __name__, url_prefix = '/bot')


@bot.route('/members', methods = ['GET'])
def user_index():
    if request.method == 'GET':
        return get_all_members()
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('/members/add', methods = ['POST'])
def create_user():
    if request.method == 'POST':
        return add_member(**request.get_json())
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('/members/<int:member_id>', methods = ['GET', 'PATCH', 'DELETE'])
def manage_user(member_id):
    if request.method == 'GET':
        return get_member(member_id)
    elif request.method == 'PATCH':
        return update_member(member_id, **request.get_json())
    elif request.method == 'DELETE':
        return remove_member(member_id, **request.get_json())
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('/guilds', methods = ['GET'])
def guild_index():
    if request.method == 'GET':
        return get_all_guilds()
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('guilds/add', methods = ['POST'])
def create_guild():
    if request.method == 'POST':
        return add_guild(**request.get_json())
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('/guilds/<int:guild_id>', methods = ['GET', 'PATCH', 'DELETE'])
def manage_guild(guild_id):
    if request.method == 'GET':
        return get_guild(guild_id)
    elif request.method == 'PATCH':
        return update_guild(guild_id, **request.get_json())
    elif request.method == 'DELETE':
        return remove_guild(guild_id)
    else:
        raise Exception('That method isn\'t allowed here.')
