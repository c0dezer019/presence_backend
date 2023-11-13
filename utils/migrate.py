from core.config import db
from core import create_app

app = create_app()


def create_tables():
    with app.app_context():
        db.create_all()


def destroy_tables():
    with app.app_context():
        db.drop_all()
