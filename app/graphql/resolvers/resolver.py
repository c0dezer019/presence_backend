# Future modules
from __future__ import annotations

# Standard modules
from typing import Sequence

# Third party modules
from fastapi import HTTPException
from sqlalchemy import Delete, Select, and_, delete, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import ReturningUpdate
from strawberry import UNSET

# Internal modules
from app.database.models import Guild, MemberShard
from app.graphql.lib.types import Snowflake
from app.utils.logging import Logger

__name__ = "__resolver__"

logger = Logger(__file__, __name__)


class Resolver:
    def __init__(self, session: Session):
        self.db = session

    def create_guilds(self, bulk_data: list[Guild]) -> Sequence[Guild]:
        try:
            logger.info("Attempting to create guilds.")

            guilds: Sequence[Guild] = Guild.bulk_create(self.db, bulk_data)

            return guilds
        except TypeError as te:
            logger.error(f"bulk_data contained incorrect data: {bulk_data}")
            logger.exception(te)

            raise HTTPException(
                500, detail=f"bulk_data contained invalid data: {bulk_data}"
            )

    def guild(
        self, guild_id: Snowflake, **kwargs
    ) -> tuple[tuple[Guild, bool], Sequence[MemberShard]]:
        logger.info("Finding or creating guild %s.", guild_id)
        try:
            guild: tuple[Guild, bool] = Guild.find_or_create(self.db, int(guild_id))

            return guild, guild[0].get_members(self.db)
        except TypeError as te:
            logger.error("TypeError while attempting to get or create %s.", guild_id)
            logger.exception(
                f"{Guild.find_or_create.__module__} received incorrect arguments:\n\n{__file__}",
                guild_id,
            )
            logger.exception(te, guild_id)

            raise HTTPException(
                status_code=500, detail=f"Incorrect arguments received: {guild_id}"
            )

    def guilds(self) -> Sequence[Guild]:
        logger.info("Fetching all guilds.")

        return Guild.get_all()

    def reset_guild(self, blame: Snowflake) -> tuple[int, bool]:
        logger.info(f"Resetting guild {blame}.")

        smtp: Delete = delete(MemberShard).where(MemberShard.guild_id == blame)
        self.db.execute(smtp).scalars().all()

        smtp2: Select[tuple[MemberShard]] = select(MemberShard).where(
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
        member_id: Snowflake,
    ) -> tuple[MemberShard, bool]:
        logger.info("Creating MemberShard %s in guild %s.", member_id, guild_id)
        try:
            guild = Guild.get_one(self.db, int(guild_id))

            if guild:
                logger.info("Guild %s found.", guild.guild_id)

            new_member = MemberShard.find_or_create(
                self.db,
                {
                    "member_id": int(member_id),
                    "guild_id": guild.id,
                },
            )

            if new_member[1]:
                logger.info(
                    "User %s created, attaching to guild %s.",
                    new_member[0].member_id,
                    guild_id,
                )

                guild.add_member(self.db, new_member[0])

                logger.info(
                    f"MemberShard #{new_member[0].id} successfully added to guild."
                )
            elif not new_member[1]:
                logger.info("Member already exists and wasn't created again.")

            return new_member
        except TypeError:
            logger.error("TypeError while attempting to add to %s.", Guild.__name__)
            logger.exception(
                "%s received incorrect arguments:\n\n%s",
                self.__module__,
                __file__,
                stack_info=True,
            )

            raise HTTPException(status_code=500, detail="Incorrect arguments received.")

    def members(self, guild_id: Snowflake):
        try:
            return MemberShard.get_all(guild_id)
        except NoResultFound as nrf:
            logger.error(f"No members for {guild_id} found.", guild_id)
            logger.exception(nrf, guild_id)

            raise HTTPException(
                status_code=404, detail=f"No members found for {guild_id}."
            )

    def update_guild(self, guild_id: Snowflake, **kwargs) -> Guild:
        try:
            logger.info(f"attempting to update guild ID {guild_id}...")

            kwargs = {str(k): v for k, v in kwargs.items() if v is not UNSET}

            upd: ReturningUpdate[tuple[Guild]] = (
                update(Guild)
                .where(Guild.guild_id == guild_id)
                .values(**kwargs)
                .returning(Guild)
            )
            guild = self.db.execute(upd).scalars().unique().one()
            self.db.commit()

            logger.info("Guild updated.")

            return guild

        except KeyError as ke:
            logger.error(f"Incorrect kwargs provided:\n\n{kwargs}", guild_id)
            logger.exception(ke, guild_id)

            raise HTTPException(
                status_code=500, detail=f"Incorrect key provided: {str(ke)}."
            )

    def update_member_shard(
        self, member_id: Snowflake, guild_id: Snowflake, **kwargs: object
    ) -> MemberShard:
        try:
            logger.info(
                "Attempting to update %s_shard ID %s...",
                MemberShard.__name__,
                member_id,
            )

            kwargs = {str(k): v for k, v in kwargs.items() if v is not UNSET}

            guild = Guild.get_one(self.db, guild_id)

            upd: ReturningUpdate[tuple[MemberShard]] = (
                update(MemberShard)
                .where(
                    and_(
                        MemberShard.guild_id == guild.id,
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

    def prune(self, guild_id: Snowflake) -> list[MemberShard] | None:
        """
        Prunes members from a guild, without deleting the guild.\n

        Params:
        guild_id: strawberry.ID
            A strawberry.ID serialized int representing the Discord Server.id.
        """

        try:
            logger.info("Getting all member_shards that belong to guild...")
            member_shards: list[MemberShard] = (
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
