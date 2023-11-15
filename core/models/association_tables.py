from sqlalchemy import Integer, ForeignKey

from ..config import sql


member_guild_association = sql.Table(
    "association_table",
    sql.Model.metadata,
    sql.Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    sql.Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
)