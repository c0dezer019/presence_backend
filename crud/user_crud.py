from flask import jsonify
from models import db, User


def get_all_users():
    all_users = User.query.all()
    results = [user.as_dict() for user in all_users]

    return jsonify(results)


def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.as_dict())
    else:
        raise Exception(f'No user at id: {user_id}')


def add_user(**kwargs):
    new_user = User(**kwargs)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.as_dict())


def update_user(user_id, **update_values):
    user = User.query.get(user_id)

    if user:
        for k, v in enumerate(update_values.items()):
            setattr(user, k, v)

        db.session.commit()

        return jsonify(user.as_dict())

    else:
        raise Exception(f'No user at id {user_id}')


def remove_user(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        raise Exception(f'No user at id {user_id}')
