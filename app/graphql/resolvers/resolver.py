# Internal modules
from __future__ import annotations

from typing import List, Optional

# Third party modules
from strawberry import ID
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError, InvalidRequestError, NoResultFound
from sqlalchemy.orm.exc import UnmappedInstanceError

# Internal modules
from app.database import Session
from app.database.models import Guild, MemberShard


class Resolver:
    def __init__(self):
        self.db = Session.Session()

    def create_guild(self, guild_id: ID, name: str) -> Guild:
        try:
            guild: Guild = Guild(guild_id=guild_id, name=name)

            self.db.add(guild)
            return guild

        except IntegrityError as ie:
            print(ie)

        except TypeError as te:
            print(te)

        self.db.commit()

    def create_member(self, guild_id: ID, guild_name: str, member_id: ID, username: str, discriminator: int,
                      nickname: Optional[str] = None) -> MemberShard:
        try:
            guild: Guild = self.db.query(Guild).where(Guild.guild_id == guild_id).where(
                Guild.name == guild_name).first()
            new_member: MemberShard = MemberShard(member_id=member_id, username=username, discriminator=discriminator,
                                                  nickname=nickname)

            guild.members.append(new_member)
            self.db.add(guild)
            self.db.add(new_member)
            self.db.commit()

            return new_member

        except InvalidRequestError as ire:
            print(ire)

    def retrieve_guild(self, guild_id: ID, name: str) -> Guild | None:
        try:
            query = self.db.query(Guild).where(Guild.guild_id == guild_id).where(Guild.name == name).first()

            return query

        except InvalidRequestError as ire:
            print(ire)

    def retrieve_member(self, member_id: ID, guild_id: ID) -> MemberShard | None:
        try:
            query = (self.db.query(MemberShard).where(MemberShard.member_id == member_id)
                     .where(MemberShard.guild_id == guild_id))

            return query
        except InvalidRequestError as ie:
            print(ie)

    def update_guild(self, guild_id: ID, **kwargs) -> Guild:
        try:
            upd = update(Guild).where(Guild.guild_id == guild_id).values(**kwargs).returning(Guild)
            res = self.db.execute(upd).unique().scalars().one()

            return res

        except NoResultFound as nrf:
            print(nrf)

    def update_member_shard(self, member_id: ID, guild_id: ID, **kwargs) -> MemberShard:
        try:
            upd = (update(MemberShard).where(MemberShard.member_id == member_id, Guild.guild_id == guild_id)
                   .values(**kwargs).returning(MemberShard))
            res = self.db.execute(upd).unique().scalars().one()

            return res
        except NoResultFound as nrf:
            print(nrf)

    def delete_guild(self, guild_id: ID) -> Guild | None:

        guild: Guild | None = self.db.query(Guild).filter_by(guild_id=guild_id).first()

        try:
            self.db.delete(guild)
            self.db.commit()
        except UnmappedInstanceError:
            pass

        return guild

    def delete_member_shard(self, guild_id: ID, member_id: ID) -> MemberShard | None:
        member_shard: Guild | None = self.db.query(MemberShard).filter(Guild.guild_id == guild_id,
                                                                       MemberShard.member_id == member_id).first()

        try:
            self.db.delete(member_shard)
            self.db.commit()
        except UnmappedInstanceError:
            pass

        return member_shard

    def prune(self, guild_id: ID) -> List[MemberShard]:
        """
        Prunes members from a guild, without deleting the guild.\n

        Params:
        guild_id: strawberry.ID
            A strawberry.ID serialized int representing the Discord Server.id.
        """

        member_shards: List[MemberShard] = self.db.query(MemberShard).filter_by(guild_id=guild_id).all()

        self.db.delete(member_shards)
        self.db.commit()

        return member_shards
