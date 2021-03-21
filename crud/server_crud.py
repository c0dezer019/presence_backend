from flask import jsonify
from server.models import db, Server


def get_all_servers():
    all_servers = Server.query.all()
    results = [server.as_dict() for server in all_servers]

    return jsonify(results)


def get_server(server_id):
    server = Server.query.get(server_id)

    if server:
        return jsonify(server.as_dict())
    else:
        raise Exception(f'No server at id: {server_id}')


def add_server(**kwargs):
    new_server = Server(**kwargs)
    db.session.add(new_server)
    db.session.commit()

    return jsonify(new_server.as_dict())


def update_server(server_id, **update_values):
    server = Server.query.get(server_id)

    if server:
        for k, v in enumerate(update_values.items()):
            setattr(server, k, v)

        db.session.commit()

        return jsonify(server.as_dict())
    else:
        raise Exception(f'No server at id {server_id}')


def remove_server(server_id):
    server = Server.query.get(server_id)

    if server:
        db.session.remove(server)
    else:
        raise Exception(f'No server at id {server_id}')
