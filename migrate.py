from core.models import db
from core import create_app

app = create_app()

with app.app_context():
    db.create_all()