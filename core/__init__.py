from dotenv import load_dotenv
from flask import Flask
from pathlib import Path
import os

env_path = Path('', '../.env')
load_dotenv(dotenv_path = env_path)


def create_app():
    flask_app = Flask(__name__, instance_relative_config = True)

    if not os.getenv('MODE'):
        flask_app.config.from_object('core.config.ProductionConfiguration')
    elif os.getenv('MODE') == 'testing':
        flask_app.config.from_object('core.config.TestConfiguration')
    elif os.getenv('MODE') == 'development':
        flask_app.config.from_object('core.config.BaseConfiguration')

    from core.models import db
    db.init_app(flask_app)

    try:
        os.makedirs(flask_app.instance_path)
    except OSError:
        pass

    from core.blueprint import bot
    flask_app.register_blueprint(bot)

    return flask_app
