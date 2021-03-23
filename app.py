from flask import Flask


def create_app(flask_config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(flask_config)

    from models import db
    db.init_app(flask_app)

    from bot_routing import bot
    flask_app.register_blueprint(bot)

    return flask_app
