from main import db
from datetime import datetime
from pytz import timezone

datetime_format = '%m/%d/%Y %H:%M:%S %Z%z'
default_time = timezone('UTC').localize(datetime(1970, 1, 1, 0, 0)).strftime('%m/%d/%Y %H:%M:%S %Z%z')

user_server_association = db.Table(
    'associationTable',
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key = True),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key = True)
)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True, nullable = False)
    username = db.Column(db.String, unique = True, nullable = False)
    last_activity = db.Column(db.String, server_default = 'None')
    last_activity_loc = db.Column(db.String, server_default = 'None')
    last_activity_ts = db.Column(db.DateTime, server_default = default_time)
    # Overall Discord status. Not representative of individual servers.
    status = db.Column(db.String, nullable = False, server_default = 'new')
    date_added = db.Column(db.DateTime, server_default = datetime.now(timezone('US/Central')).strftime(datetime_format))

    def __repr__(self):
        return f'<User(id = {self.id}, username = {self.username}, last_activity = {self.last_activity},' \
               f' last_activity_loc = {self.last_activity_loc}, last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }


class Server(db.Model):
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    last_activity = db.Column(db.String, server_default = 'None')
    last_activity_ts = db.Column(db.DateTime, server_default = default_time)
    status = db.Column(db.String, nullable = False, server_default = 'new')
    users = db.relationship(User, secondary = user_server_association, lazy = 'subquery',
                            backref = db.backref('servers', lazy = True))
    date_added = db.Column(db.DateTime, server_default = datetime.now(timezone('US/Central')).strftime(datetime_format))

    def __repr__(self):
        return f'<User(id = {self.id}, server = {self.name}, last_activity = {self.last_activity},' \
               f' last_activity_ts = {self.last_activity_ts})>'

    def as_dict(self):
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

# s = Server()
# u = User()
# s.users.append(u)
# db.session.add(s)
# db.session.commit()
