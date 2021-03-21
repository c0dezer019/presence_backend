from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
from crud.user_crud import add_user, get_user, get_all_users, update_user, remove_user
from crud.server_crud import add_server, get_server, get_all_servers, update_server, remove_server
from settings import env, mode

env = env[mode]
USER = env['USER']
PASS = env['PASS']
HOST = env['HOST']
PORT = env['PORT']
DB = env['DB']


class PSQLAlchemy(SQLAlchemy):
    Column: Callable
    Integer: Callable
    String: Callable
    DateTime: Callable
    Table: Callable
    ForeignKey: Callable
    relationship: Callable
    backref: Callable


db = PSQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASS}@{HOST}:{PORT}/{DB}'

    @app.route('/users', methods = ['POST', 'GET'])
    def user_index():
        if request.method == 'GET':
            return get_all_users()
        elif request.method == 'POST':
            return add_user(**request.form)
        else:
            raise Exception('That method isn\'t allowed here.')

    @app.route('/users/<int:user_id>', methods = ['GET', 'PUT', 'DELETE'])
    def manage_user(user_id):
        if request.method == 'GET':
            return get_user(user_id)
        elif request.method == 'PUT':
            return update_user(user_id, **request.form)
        elif request.method == 'DELETE':
            return remove_user(user_id)
        else:
            raise Exception('That method isn\'t allowed here.')

    @app.route('/servers', methods = ['POST', 'GET'])
    def server_index():
        if request.method == 'GET':
            return get_all_servers()
        elif request.method == 'POST':
            return add_server(**request.form)
        else:
            raise Exception('That method isn\'t allowed here.')

    @app.route('/servers/<int:server_id>', methods = ['GET', 'PUT', 'DELETE'])
    def manage_server(server_id):
        if request.method == 'GET':
            return get_server(server_id)
        elif request.method == 'PUT':
            return update_server(server_id, **request.form)
        elif request.method == 'DELETE':
            return remove_server(server_id)
        else:
            raise Exception('That method isn\'t allowed here.')

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error('Unhandled Exception: %s', e)
        message_str = e.__str__()

        return jsonify(message = message_str.split(':')[0])

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
