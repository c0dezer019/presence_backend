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
    db.Column('member_id', db.Integer, db.ForeignKey('members.id'), primary_key = True),
    db.Column('guild_id', db.Integer, db.ForeignKey('guilds.id'), primary_key = True)
)


class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key = True, nullable = False)
    user_id = db.Column(db.BigInteger, nullable = False, unique = True)
    username = db.Column(db.String, unique = True, nullable = False)
    admin_access = db.Column(db.Boolean, default = False)
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

    def update(self, new_timestamp):
        self.last_activity_ts = new_timestamp


class Guild(db.Model):
    __tablename__ = 'guilds'

    id = db.Column(db.Integer, primary_key = True)
    guild_id = db.Column(db.BigInteger, nullable = False, unique = True)
    name = db.Column(db.String, nullable = False)
    last_activity = db.Column(db.String, server_default = 'None')
    last_activity_ts = db.Column(db.DateTime(timezone = True))
    status = db.Column(db.String, nullable = False, server_default = 'new')
    settings = db.Column(db.JSON, default = { })
    members = db.relationship(User, secondary = user_server_association, lazy = 'subquery',
                              backref = db.backref('guilds', lazy = True))
    date_added = db.Column(db.DateTime(timezone = True), default = datetime.now(timezone('US/Central')))

    def __repr__(self):
        return f'<Server(id = {self.id}, name = {self.name}, last_activity = {self.last_activity},' \
               f' last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }
