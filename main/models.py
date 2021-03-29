from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
from pytz import timezone


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

user_server_association = db.Table(
    'associationTable',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key = True),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key = True)
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, nullable = False)
    user_id = db.Column(db.Integer, nullable = False, unique = True)
    username = db.Column(db.String, unique = True, nullable = False)
    last_activity = db.Column(db.String, server_default = 'None')
    last_activity_loc = db.Column(db.String, server_default = 'None')
    last_activity_ts = db.Column(db.DateTime(timezone = True), default = datetime(1970, 1, 1, 0, 0))
    # Overall Discord status. Not representative of individual servers.
    status = db.Column(db.String, nullable = False, server_default = 'new')
    date_added = db.Column(db.DateTime(timezone = True), default = datetime.now(timezone('US/Central')))

    def __repr__(self):
        return f'<User(id = {self.id}, user_id = {self.user_id}, username = {self.username}, ' \
               f' last_activity = {self.last_activity}, last_activity_loc = {self.last_activity_loc}, ' \
               f' last_activity_ts = {self.last_activity_ts}), status = {self.status}, date_added = {self.date_added}>'

    def as_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }


class Server(db.Model):
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key = True)
    server_id = db.Column(db.Integer, nullable = False, unique = True)
    name = db.Column(db.String, nullable = False)
    last_activity = db.Column(db.String, server_default = 'None')
    last_activity_ts = db.Column(db.DateTime(timezone = True), default = datetime(1970, 1, 1, 0, 0))
    status = db.Column(db.String, nullable = False, server_default = 'new')
    users = db.relationship(User, secondary = user_server_association, lazy = 'subquery',
                            backref = db.backref('servers', lazy = True))
    date_added = db.Column(db.DateTime(timezone = True), default = datetime.now(timezone('US/Central')))

    def __repr__(self):
        return f'<Server(id = {self.id}, name = {self.name}, last_activity = {self.last_activity},' \
               f' last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }
