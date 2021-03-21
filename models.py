from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
from settings import environment, mode


env = environment[0] if mode == 'development' else environment[1]
USER = env['USER']
PASS = env['PASS']
HOST = env['HOST']
PORT = env['PORT']
DB = env['DB']

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{USER}:{PASS}@{HOST}:{PORT}/{DB}'


class PSQLAlchemy(SQLAlchemy):
    Column: Callable
    Integer: Callable
    String: Callable
    DateTime: Callable
    Table: Callable
    ForeignKey: Callable
    relationship: Callable
    backref: Callable


db = PSQLAlchemy(app)

user_server = db.Table(
    'user_server',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True),
    db.Column('server_id', db.Integer, db.ForeignKey('server.id'), primary_key = True)
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, nullable = False)
    username = db.Column(db.String, unique = True, nullable = False)
    servers = db.relationship(
        'Server',
        secondary = user_server,
        lazy = 'subquery',
        backref = db.backref('pages', lazy = True))
    last_activity = db.Column(db.String)
    last_activity_loc = db.Column(db.String)
    last_activity_ts = db.Column(db.DateTime)
    # Overall Discord status. Not representative of individual servers.
    status = db.Column(db.String, nullable = False)

    def __repr__(self):
        return f'<User(id = {self.id}, username = {self.username}, last_activity = {self.last_activity},' \
               f' last_activity_loc = {self.last_activity_loc}, last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Server(db.Model):
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String, nullable = False)
    last_activity = db.Column(db.String)
    last_activity_ts = db.Column(db.DateTime)
    status = db.Column(db.String, nullable = False)

    def __repr__(self):
        return f'<User(id = {self.id}, server = {self.name}, last_activity = {self.last_activity},' \
               f' last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



