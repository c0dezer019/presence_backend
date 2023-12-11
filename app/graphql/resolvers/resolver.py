# Internal modules
from __future__ import annotations

from typing import List, Optional, Type

from fastapi import HTTPException
# Third party modules
from sqlalchemy import update, Update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import UnmappedInstanceError

# Internal modules
from app.database import ORMSession
from app.database.models import Guild, MemberShard
from app.database.utils import get_or_create


class Resolver:
    def __init__(self):
        self.db = ORMSession

    def guild(self, guild_id: int, name: str) -> Guild:
        guild: tuple[Guild, bool] = get_or_create(self.db.session, Guild, guild_id=guild_id, name=name)

        return guild[0]

    def member(self, guild_id: int, guild_name: str, member_id: int, username: str, discriminator: int,
               nickname: Optional[str] = None) -> MemberShard:

        guild: Guild | None = self.db.session.query(Guild).where(Guild.guild_id == guild_id).where(
            Guild.name == guild_name
        ).first()
        new_member: tuple[Guild | MemberShard, bool] = \
            get_or_create(self.db.session, MemberShard, member_id=member_id, username=username,
                          discriminator=discriminator, nickname=nickname)

        if new_member[1]:
            guild.members.append(new_member[0])
            self.db.session.add(guild)
            self.db.session.commit()

        return new_member[0]

    def update_guild(self, guild_id: int, **kwargs) -> Guild:
        try:
            upd = update(Guild).where(Guild.guild_id == guild_id).values(**kwargs).returning(Guild)
            res = self.db.session.execute(upd).unique().scalars().one()

            return res

        except NoResultFound as nrf:
            print(nrf)

    def update_member_shard(self, member_id: int, guild_id: int, **kwargs) -> MemberShard:
        try:
            upd: Update = (update(MemberShard).where(MemberShard.member_id == member_id, Guild.guild_id == guild_id)
                           .values(**kwargs).returning(MemberShard))
            res: MemberShard = self.db.session.execute(upd).unique().scalars().one()

            return res
        except NoResultFound as nrf:
            print(nrf)

    def delete_guild(self, guild_id: int) -> Guild | None:

        guild: Guild | None = self.db.session.query(Guild).filter_by(guild_id=guild_id).first()

        try:
            self.db.session.delete(guild)
            self.db.session.commit()
        except UnmappedInstanceError:
            pass

        return guild

    def delete_member_shard(self, guild_id: int, member_id: int) -> MemberShard | None:
        member_shard: Guild | None = (self.db.session.query(MemberShard)
                                      .filter(Guild.guild_id == guild_id, MemberShard.member_id == member_id)
                                      .first())

        try:
            self.db.session.delete(member_shard)
            self.db.session.commit()
        except UnmappedInstanceError:
            pass

        return member_shard

    def prune(self, guild_id: int) -> List[Type[MemberShard]]:
        """
        Prunes members from a guild, without deleting the guild.\n

        Params:
        guild_id: strawberry.ID
            A strawberry.ID serialized int representing the Discord Server.id.
        """

        member_shards: List[Type[MemberShard]] = self.db.query(MemberShard).filter_by(guild_id=guild_id).all()

        self.db.session.delete(member_shards)
        self.db.session.commit()

        return member_shards
