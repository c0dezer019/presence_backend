from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, BigInteger, Boolean, Column, DateTime, Integer, ForeignKey, JSON, String
from sqlalchemy.orm import DeclarativeBase
from arrow import get, now


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

member_guild_association = db.Table(
    "associationTable",
    db.Model.metadata,
    Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
)


class Member(db.Model):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    discriminator = Column(Integer, nullable=False, unique=True)
    member_id = Column(BigInteger, nullable=False, unique=True)
    nickname = Column(String, server_default=f"{username}")
    admin_access = Column(Boolean, default=False)
    last_activity = Column(String, server_default="None")
    last_active_server = Column(BigInteger, default=0)
    last_active_channel = Column(BigInteger, default=0)
    last_active_ts = Column(
        DateTime(timezone=True), default=get(datetime(1970, 1, 1, 0, 0)).datetime
    )
    idle_times = Column(ARRAY(Integer), default=[])
    # Instant avg like an instant MPG in the car.
    avg_idle_time = Column(Integer, default=0)
    recent_avgs = Column(ARRAY(Integer), default=[])
    # Overall Discord status. Not representative of individual servers.
    status = Column(String, nullable=False, server_default="new")
    date_added = Column(
        db.DateTime(timezone=True), default=now("US/Central").datetime
    )

    def __repr__(self):
        return (
            f"<Member (id = {self.id}, username = {self.username}, user_tag = {self.discriminator}"
            f"member_id = {self.member_id}, last_activity = {self.last_activity}, "
            f"last_active_server = {self.last_active_server}, last_active_channel = "
            f"{self.last_active_channel} last_active_ts = {self.last_active_ts.isoformat()}), "
            f"idle_times = {self.idle_times}, avg_idle_time = {self.avg_idle_time}, "
            f"recent_avgs = {self.recent_avgs}, status = {self.status}, date_added = "
            f"{self.date_added.isoformat()}>"
        )

    def as_dict(self):
        member_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns} # type: ignore
        member_dict["last_activity_ts"] = member_dict["last_activity_ts"].isoformat()
        member_dict["date_added"] = member_dict["date_added"].isoformat()

        return member_dict

    def update(self, new_timestamp):
        self.last_active_ts = new_timestamp


class Guild(db.Model):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BigInteger, nullable=False, unique=True)
    name = Column(String, nullable=False)
    last_activity = Column(String, server_default="None")
    last_active_channel = Column(BigInteger, default=0)
    last_active_ts = Column(
        db.DateTime(timezone=True), default=get(datetime(1970, 1, 1, 0, 0)).datetime
    )
    idle_times = Column(ARRAY(Integer), default=[])
    avg_idle_time = Column(Integer, nullable=True, default=0)
    recent_avgs = Column(ARRAY(Integer), default=[])
    status = Column(String, nullable=False, server_default="new")
    settings = Column(JSON, default={})
    members = db.relationship(
        Member,
        secondary=member_guild_association,
        lazy="joined",
        backref=db.backref("guilds", lazy=True),
    )
    date_added = Column(
        db.DateTime(timezone=True), default=now("US/Central").datetime
    )

    def __repr__(self):
        return (
            f"<Guild (id = {self.id}, guild_id = {self.guild_id},  name = {self.name}, "
            f"last_activity = {self.last_activity}, last_active_channel = "
            f"{self.last_active_channel}, last_active_ts = {self.last_active_ts}, idle_times = "
            f"{self.idle_times} avg_idle_time = {self.avg_idle_time}, recent_avgs = "
            f"{self.recent_avgs}, status = {self.status}, settings = {self.settings}, members = "
            f"{self.members}, date_added = {self.date_added.isoformat()})>"
        )

    def as_dict(self):
        guild_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        guild_dict["last_activity_ts"] = guild_dict["last_activity_ts"].isoformat()
        guild_dict["date_added"] = guild_dict["date_added"].isoformat()
        guild_dict["members"] = []

        for member in self.members:
            member_dict = member.as_dict()
            guild_dict["members"].append(member_dict)

        return guild_dict
