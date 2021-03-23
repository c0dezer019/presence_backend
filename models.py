from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from typing import Callable


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
    'user_server_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key = True),
    db.Column('server_id', db.Integer, db.ForeignKey('server.id'), primary_key = True)
)


class Server(db.Model):
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String, nullable = False)
    last_activity = db.Column(db.String, default = 'None')
    last_activity_ts = db.Column(db.DateTime, default = datetime(1970, 1, 1, 0, 0))
    status = db.Column(db.String, nullable = False, default = 'new')
    users = db.relationship("User", secondary = user_server_association, lazy = 'subquery',
                            backref = db.backref('servers', lazy = True))
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return f'<User(id = {self.id}, server = {self.name}, last_activity = {self.last_activity},' \
               f' last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, nullable = False)
    username = db.Column(db.String, unique = True, nullable = False)
    last_activity = db.Column(db.String, default = 'None')
    last_activity_loc = db.Column(db.String, default = 'None')
    last_activity_ts = db.Column(db.DateTime, default = datetime(1970, 1, 1, 0, 0))
    # Overall Discord status. Not representative of individual servers.
    status = db.Column(db.String, nullable = False, default = 'new')
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return f'<User(id = {self.id}, username = {self.username}, last_activity = {self.last_activity},' \
               f' last_activity_loc = {self.last_activity_loc}, last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

# s = Server()
# u = User()
# s.users.append(u)
# db.session.add(s)
# db.session.commit()
