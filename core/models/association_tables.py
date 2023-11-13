from sqlalchemy import Integer, ForeignKey

from ..config import db


member_guild_association = db.Table(
    "association_table",
    db.Model.metadata,
    db.Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    db.Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
)