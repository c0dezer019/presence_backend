from sqlalchemy import Integer, ForeignKey

from core.config import sql


members_guilds = sql.Table(
    "members_guilds",
    sql.Model.metadata,
    sql.Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    sql.Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
)