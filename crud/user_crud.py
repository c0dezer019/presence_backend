from flask import jsonify
from main.models import db
from main.models import User, Server


def get_all_users():
    all_users = User.query.all()
    results = [user.as_dict() for user in all_users]

    return jsonify(results)


def get_user(user_id):
    user = User.query.filter_by(user_id = user_id).first()
    if user:
        return jsonify(user.as_dict())
    else:
        raise Exception(f'No user at id: {user_id}')


def add_user(**data):

    user = User.query.filter_by(user_id = data['user_id']).first()
    server = Server.query.filter_by(server_id = data['server_id']).first()

    if not user:
        try:
            user = User(user_id = data['user_id'], username = data['username'])

            server.users.append(user)
            db.session.add(user)
            db.session.commit()

        except ValueError:
            return f'Server with id #{data["server_id"]} not found.', 404

        except AttributeError:
            return 'An association error has occurred.', 400

        else:
            return jsonify(user.as_dict())
    else:
        server.users.append(user)
        db.session.add(user)
        db.session.commit()

        return jsonify(server.as_dict())


def update_user(user_id, **data):
    user = User.query.filter_by(user_id = user_id).first()

    if user:
        for k, v in data.items():
            if k != 'act_timestamp':
                setattr(user, k, v)
            else:
                setattr(user, k, v.fromisoformat())

        db.session.commit()

        return jsonify(user.as_dict())
    else:
        raise Exception(f'No user at id {user_id}')


def remove_user(user_id, **data):
    user = User.query.filter_by(user_id = user_id).first()

    if user:
        for v in data.keys():
            if v != 'hard_delete':
                server = Server.query.filter_by(**data).first()

                if server:
                    server.users.remove(user)
                    db.session.commit()

                    return f'User {user.username}(id #{user.user_id}) successfully removed from server {server.name}' \
                           f'(id #{server.server_id}).', 200
                else:
                    raise Exception('A valid server was not provided.')
        else:
            db.session.delete(user)
            db.session.commit()

            return f' User {user.username}(id #{user.user_id}) successfully purged from database.', 200
    else:
        raise Exception(f'Nothing found with the args: {data}')
