from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
import os


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


def create_app(flask_config = None):
    flask_app = Flask(__name__, instance_relative_config = True)
    flask_app.config.from_mapping(
        SECRET = os.getenv('SECRET'),
        DATABASE = os.path.join(flask_app.instance_path, 'main.config'),
    )

    if flask_config is None:
        flask_app.config.from_pyfile('config.BaseConfiguration', silent = True)
    else:
        flask_app.config.from_mapping(flask_config)

    try:
        os.makedirs(flask_app.instance_path)
    except OSError:
        pass

    from bot_routing import bot
    flask_app.register_blueprint(bot)

    return flask_app
