from flask import Blueprint, jsonify, request
from crud.user_crud import add_user, get_user, get_all_users, update_user, remove_user
from crud.server_crud import add_server, get_server, get_all_servers, update_server, remove_server


bot = Blueprint('bot', __name__, url_prefix = '/bot')


@bot.route('/users', methods = ['POST', 'GET'])
def user_index():
    if request.method == 'GET':
        return get_all_users()
    elif request.method == 'POST':
        return add_user(data = request.get_json())
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('/users/<int:user_id>', methods = ['GET', 'PATCH', 'DELETE'])
def manage_user(user_id):
    if request.method == 'GET':
        return get_user(user_id)
    elif request.method == 'PATCH':
        return update_user(user_id, **request.get_json())
    elif request.method == 'DELETE':
        return remove_user(user_id, **request.get_json())
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('/servers', methods = ['POST', 'GET'])
def server_index():
    if request.method == 'GET':
        return get_all_servers()
    elif request.method == 'POST':
        return add_server(**request.get_json())
    else:
        raise Exception('That method isn\'t allowed here.')


@bot.route('/servers/<int:server_id>', methods = ['GET', 'PATCH', 'DELETE'])
def manage_server(server_id):
    if request.method == 'GET':
        return get_server(server_id)
    elif request.method == 'PATCH':
        return update_server(server_id, **request.get_json())
    elif request.method == 'DELETE':
        return remove_server(server_id)
    else:
        raise Exception('That method isn\'t allowed here.')
