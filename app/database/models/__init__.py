from sqlalchemy.ext.declarative import declarative_base

from .guild import Guild # noqa: F401
from .member_shard import MemberShard  # noqa: F401

Base = declarative_base()