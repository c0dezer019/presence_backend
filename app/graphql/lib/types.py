# Future modules
from __future__ import annotations

# Standard modules
from typing import NewType, Tuple

# Third party modules
from sqlalchemy import Row, Sequence

# Internal modules
from app.database.models import Guild, MemberShard

Snowflake = NewType('Snowflake', int)
Discriminator = NewType('Discriminator', int)
type Model = Guild | MemberShard
type GuildRow = Row[tuple[Snowflake, str]] | None
type MemberShardRow = Row[tuple[Snowflake, str, Discriminator]] | None
type DBRow = GuildRow | MemberShardRow
type Query = Tuple[DBRow, bool]
type QueryAll = Sequence[MemberShard | Guild]
