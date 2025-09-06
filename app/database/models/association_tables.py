# Third party modules
from sqlalchemy import Column, ForeignKey, Integer, Table

# Internal modules
from app.database.models import BaseModel

members_guilds = Table(
    "members_guilds",
    BaseModel.metadata,
    Column("member_id", Integer, ForeignKey("members.id"), primary_key=True),
    Column("guild_id", Integer, ForeignKey("guilds.id"), primary_key=True),
)
