from app import create_app
from models import db


if __name__ == '__main__':
    app = create_app('config.BaseConfiguration')
    db.init_app(app)
    print('All set up!')
