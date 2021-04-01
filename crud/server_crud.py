from flask import jsonify
from main.models import db
from main.models import Server
import jsonify


# *      * #
#  Create  #
# *      * #
def add_server(**kwargs):
    try:
        new_server = Server(**kwargs)
        db.session.add(new_server)
        db.session.commit()

        return jsonify(new_server.as_dict())

    except Exception:
        raise Exception('Something went wrong while adding new server.')


# *         * #
#   Retrieve  #
# *         * #
def get_all_servers():
    try:
        all_servers = Server.query.all()
        results = [server.as_dict() for server in all_servers]

    except ValueError:
        raise Exception('No data exists in the database.')

    else:
        return jsonify(results)


def get_server(server_id):
    try:
        server = Server.query.filter_by(server_id = server_id).first()
        return jsonify(server.as_dict()), 200
    except ValueError:
        return 'Could not retrieve specified server.', 404
    except AttributeError:
        return 'Tried working with an improper datatype', 400


# *      * #
#  Update  #
# *      * #
def update_server(server_id, **data):
    try:
        server = Server.query.filter_by(server_id = server_id).first()

        for k, v in data.items():
            setattr(server, k, v)
        db.session.commit()

    except AttributeError:
        raise Exception('Tried passing incorrect attribute to server.')

    except ValueError:
        return f'No server found with id #{data["server_id"]}.', 404

    except TypeError:
        raise Exception('Bot tried to do something obscene with an object.')

    else:
        return f'Server name {server.name} with id #{server.server_id} successfully updated.', 200


# *      * #
#  Delete  #
# *      * #
def remove_server(server_id):
    try:
        server = Server.query.filter_by(server_id = server_id).first()

        db.session.delete(server)
        db.session.commit()

    except ValueError:
        raise Exception(f'No server at id {server.server_id}')

    else:
        return f'Server name {server.name} with id #{server.server_id} successfully deleted.', 200
