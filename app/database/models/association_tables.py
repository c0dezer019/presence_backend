from sqlalchemy import Column, Integer, ForeignKey, Table

from app.database.database import Base


members_guilds = Table(
    "members_guilds",
    Base.metadata,
    Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
)