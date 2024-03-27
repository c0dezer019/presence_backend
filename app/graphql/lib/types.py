from __future__ import annotations

from typing import NewType, Tuple

from sqlalchemy import Row, Sequence

from app.database.models import Guild, MemberShard

Snowflake = NewType('Snowflake', int)
Discriminator = NewType('Discriminator', int)
type Model = Guild | MemberShard
type GuildRow = Row[tuple[Snowflake, str]] | None
type MemberShardRow = Row[tuple[Snowflake, str, Discriminator]] | None
type DBRow = GuildRow | MemberShardRow
type Query = Tuple[DBRow, bool] | Tuple[Guild | MemberShard, bool]
type QueryAll = Sequence[MemberShard | Guild]
