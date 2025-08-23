# Internal modules
from __future__ import annotations

# External modules
from typing import List, Optional, Type, Tuple, Sequence, cast

from fastapi import HTTPException
from sqlalchemy import Delete, Select, delete, update, select, and_
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.sql.dml import ReturningUpdate

# Internal modules
from app.database.models import Guild, MemberShard
from app.database.utils import (
    get_or_create_one,
    get_all,
    create_one_guild,
    bulk_create_guilds,
)
from app.graphql.lib.types import DBRow, Discriminator, Snowflake
from app.utils.logging import rel, Logger

__name__ = "__resolver__"

logger = Logger(__file__, __name__)


class Resolver:
    def __init__(self, session: Session):
        self.db = session

    def create_guild(
        self, guild_id: Snowflake, name: str, **kwargs
    ) -> Tuple[int, Guild]:
        logger.info(f"Creating guild {name}.")

        try:
            guild: Guild = create_one_guild(self.db, guild_id, name, **kwargs)

            return 200, guild
        except TypeError:
            logger.error(f"TypeError while attempting to create {Guild.__qualname__}.")
            logger.exception(
                f"{create_one_guild.__module__} received incorrect arguments:\n\n{__file__}"
            )

            raise HTTPException(
                status_code=500, detail=f"Incorrect arguments received: {kwargs}."
            )

        except FlushError as fe:
            logger.exception(f"{rel(__file__)}.{create_one_guild.__name__}: {fe}")

            raise HTTPException(500, f"Error while flushing: {fe}")

        except IntegrityError as ie:
            logger.exception(
                f"{rel(__file__)}.{create_one_guild.__name__}: {ie.detail}"
            )

            raise HTTPException(
                409,
                detail=f"{rel(__file__)}.{create_one_guild.__name__} ({create_one_guild.__module__}): "
                f"{ie.detail}",
            )

    def create_guilds(self, bulk_data: List[Guild]) -> Tuple[int, Sequence[Guild]]:
        try:
            logger.info("Attempting to create guilds.")

            guilds: Sequence[Guild] = bulk_create_guilds(self.db, bulk_data)
            logger.info("Guilds created")

            return 200, guilds
        except TypeError as te:
            logger.error(f"bulk_data contained incorrect data: {bulk_data}")
            logger.exception(te)

            raise HTTPException(
                500, detail=f"bulk_data contained invalid data: {bulk_data}"
            )

    def guild(self, guild_id: Snowflake, name: str) -> Tuple[int, Guild]:
        logger.info(f"Finding or creating guild {name}.")
        try:
            guild: DBRow | Guild | MemberShard = get_or_create_one(
                self.db, Guild, cast(str, guild_id), guild_id=guild_id, name=name
            )[0]

            return 200, cast(Guild, guild)
        except TypeError as te:
            logger.error(
                f"TypeError while attempting to get or create {name} ({guild_id})."
            )
            logger.exception(
                f"{get_or_create_one.__module__} received incorrect arguments:\n\n{__file__}",
                guild_id,
            )
            logger.exception(te, guild_id)

            raise HTTPException(
                status_code=500,
                detail=f"Incorrect arguments received: "
                f'{"guild_id": {guild_id}, "name": {name}}',
            )

        except IntegrityError as ie:
            logger.error(f"Integral error while creating guild {name} ({guild_id}).")
            logger.exception(ie, guild_id)

            raise HTTPException(
                status_code=409,
                detail=f"{rel(__file__)}.{get_or_create_one.__name__} ({get_or_create_one.__module__}): {ie.detail}",
            )

    def guilds(self, blame: Snowflake):
        logger.info("Fetching all guilds.")

        return get_all(self.db, Guild, blame=blame)

    def reset_guild(self, blame: Snowflake) -> tuple[int, bool]:
        logger.info(f"Resetting guild {blame}.")

        smtp: Delete = delete(MemberShard).where(MemberShard.guild_id == blame)
        self.db.execute(smtp).scalars().all()

        smtp2: Select[Tuple[MemberShard]] = select(MemberShard).where(
            MemberShard.guild_id == blame
        )
        members: Sequence[MemberShard] = self.db.execute(smtp2).scalars().unique().all()

        if not members:
            logger.error(f"Failed to reset guild {blame}.")
            logger.exception(
                f"Failed to reset guild {blame}.", blame, exc_info=True, stack_info=True
            )

            raise HTTPException(
                status_code=409,
                detail=f"Reset of guild {blame} has failed for unknown reason.",
            )

        return 200, True

    def member(
        self,
        guild_id: Snowflake,
        guild_name: str,
        member_id: Snowflake,
        username: str,
        discriminator: Optional[Discriminator] = None,
        nickname: Optional[str] = "",
    ) -> MemberShard | None:
        logger.info(
            f"Creating MemberShard for {username} in guild {guild_name} ({guild_id})."
        )
        logger.info(f"Searching for guild {guild_id}...")

        member = None

        try:
            guild: Tuple[Guild, bool] = cast(
                Tuple[Guild, bool],
                get_or_create_one(
                    self.db,
                    Guild,
                    cast(str, guild_id),
                    guild_id=guild_id,
                    guild_name=guild_name,
                ),
            )

            if guild[1] is False:
                logger.info(f"Guild {guild[0].guild_id} found as {guild[0].name}.")
            else:
                logger.warning(
                    f"Guild {guild[0].name}({guild[0].guild_id}) was not in the db and was created."
                )

            new_member: Tuple[MemberShard, bool] = cast(
                Tuple[MemberShard, bool],
                get_or_create_one(
                    self.db,
                    MemberShard,
                    cast(str, guild_id),
                    member_id=member_id,
                    username=username,
                    discriminator=discriminator,
                    nickname=nickname,
                ),
            )

            if new_member[1]:
                logger.info(
                    f"User {new_member[0].id} created, attaching to guild {guild[0].name}."
                )

                guild[0].members.append(new_member[0])
                self.db.add(guild)
                self.db.commit()

                logger.info(
                    f"MemberShard #{new_member[0].id} successfully added to guild."
                )

                member = new_member[0]
            elif not new_member[1]:
                logger.info("Member already exists and wasn't created again.")

                member = new_member[0]
        except TypeError:
            logger.error(f"TypeError while attempting to add to {Guild.__qualname__}.")
            logger.exception(
                f"{self.__module__} received incorrect arguments:\n\n{__file__}",
                stack_info=True,
            )

            raise HTTPException(status_code=500, detail="Incorrect arguments received.")
        except IntegrityError as ie:
            logger.exception(
                f"{rel(__file__)}.{get_or_create_one.__name__}: {ie.detail}",
                stack_info=True,
            )

            raise HTTPException(
                status_code=500,
                detail=f"{rel(__file__)}.{self.member.__name__} ({self.__module__}): {ie.detail}",
            )
        finally:
            return member

    def members(self, guild_id: Snowflake):
        try:
            return get_all(self.db, MemberShard, guild_id)
        except NoResultFound as nrf:
            logger.error(f"No members for {guild_id} found.", guild_id)
            logger.exception(nrf, guild_id)

            raise HTTPException(
                status_code=404, detail=f"No members found for {guild_id}."
            )

    def update_guild(self, guild_id: Snowflake, **kwargs) -> Tuple[int, Guild]:
        try:
            logger.info(f"attempting to update guild ID {guild_id}...")

            upd: ReturningUpdate[Tuple[Guild]] = (
                update(Guild)
                .where(Guild.guild_id == guild_id)
                .values(**kwargs)
                .returning(Guild)
            )
            guild = self.db.execute(upd).scalars().unique().one()
            self.db.commit()

            logger.info("Guild updated.")

            return 200, guild

        except KeyError as ke:
            logger.error(f"Incorrect kwargs provided:\n\n{kwargs}", guild_id)
            logger.exception(ke, guild_id)

            raise HTTPException(
                status_code=500, detail=f"Incorrect key provided: {str(ke)}."
            )

    def update_member_shard(
        self, member_id: Snowflake, guild: Type[Guild], **kwargs: object
    ) -> MemberShard | None:
        kwargs = {str(k): v for k, v in kwargs}

        try:
            logger.info(f"attempting to update member_shard ID {member_id}...")

            upd: ReturningUpdate[Tuple[MemberShard]] = (
                update(MemberShard)
                .where(
                    and_(
                        MemberShard.guild_id == guild.guild_id,
                        MemberShard.member_id == member_id,
                    )
                )
                .values(**kwargs)
                .returning(MemberShard)
            )
            res = self.db.execute(upd).scalars().one()

            logger.info(f"Member {res.id} updated.")

            return res

        except NoResultFound as nrf:
            logger.error(f"Cannot find member {member_id}.")

            raise HTTPException(
                status_code=404, detail=f"Could not find member {member_id}: {str(nrf)}"
            )

    def delete_guild(self, guild_id: Snowflake) -> Guild:
        try:
            logger.info(f"Attempting to delete guild ID {guild_id}...")

            guild: Guild | None = (
                self.db.execute(select(Guild).where(Guild.guild_id == guild_id))
                .unique()
                .scalar_one()
            )

            logger.info(f"Guild {guild.id} found. Deleting...")

            self.db.delete(guild)
            self.db.commit()

            return guild

        except NoResultFound as nrf:
            logger.error(f"Cannot find guild {guild_id}.", src=guild_id)
            logger.exception(nrf, stack_info=True, exc_info=True, src=guild_id)

            raise HTTPException(
                status_code=404, detail=f"Could not find guild {guild_id}."
            )

    def delete_member_shard(
        self, guild_id: Snowflake, member_id: Snowflake
    ) -> MemberShard | None:
        try:
            logger.info("Attempting to delete member....")
            member_shard: MemberShard = (
                self.db.execute(
                    select(MemberShard).where(
                        and_(
                            Guild.guild_id == guild_id,
                            MemberShard.member_id == member_id,
                        )
                    )
                )
                .unique()
                .scalar_one()
            )

            if member_shard is not None:
                logger.info(f"member_shard {member_shard.id} found. Deleting...")

            self.db.delete(member_shard)
            self.db.commit()

            return member_shard
        except NoResultFound as nrf:
            logger.error(f"Cannot find member {member_id}.", guild_id)
            logger.exception(nrf, guild_id)

            raise HTTPException(
                status_code=404,
                detail=f"Could not find member {member_id}: {str(nrf)}.",
            )

    def prune(self, guild_id: Snowflake) -> List[MemberShard] | None:
        """
        Prunes members from a guild, without deleting the guild.\n

        Params:
        guild_id: strawberry.ID
            A strawberry.ID serialized int representing the Discord Server.id.
        """

        try:
            logger.info("Getting all member_shards that belong to guild...")
            member_shards: List[MemberShard] = (
                self.db.query(MemberShard).filter_by(guild_id=guild_id).all()
            )

            if len(member_shards) > 0:
                logger.info(f"Found {len(member_shards)} member_shards.")

            self.db.delete(member_shards)
            self.db.commit()

            return member_shards

        except NoResultFound as nrf:
            logger.error(
                "No members to delete. If there are supposed to be members, check to see if they exist.",
                guild_id,
            )
            logger.exception(nrf, guild_id)
