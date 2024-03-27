# Internal modules
from __future__ import annotations

# External modules
from typing import List, Optional, Type, Tuple

from fastapi import HTTPException
from sqlalchemy import update, select, and_, Sequence
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError
from sqlalchemy.sql.dml import ReturningUpdate

# Internal modules
from app.database.models import Guild, MemberShard
from app.database.utils import get_or_create_one, get_all, create_one_guild, bulk_create_guilds
from app.graphql.lib.types import Discriminator, Snowflake
from app.utils.logging import rel, Logger

__name__ = '__resolver__'

logger = Logger(__file__, __name__)


class Resolver:
    def __init__(self, session: Session):
        self.db = session

    def create_guild(self, guild_id: Snowflake, name: str, **kwargs) -> Tuple[int, Guild]:
        logger.info(f'Creating guild {name}.')

        try:
            guild: Guild = create_one_guild(self.db, Guild, guild_id, name, **kwargs)

            return 200, guild
        except TypeError:
            logger.error(f'TypeError while attempting to create {Guild.__qualname__}.')
            logger.exception(f'{create_one_guild.__module__} received incorrect arguments:\n\n{__file__}')

            raise HTTPException(status_code=500, detail=f'Incorrect arguments received: {kwargs}.', traceback=True)

        except FlushError as fe:
            logger.exception(f'{rel(__file__)}.{create_one_guild.__name__}: {fe}')

            raise HTTPException(500, f'Error while flushing: {fe}', traceback=True)

        except IntegrityError as ie:
            logger.exception(f'{rel(__file__)}.{create_one_guild.__name__}:' f' {ie.detail}')

            raise HTTPException(409,
                                detail=f'{rel(__file__)}.{create_one_guild.__name__} ({create_one_guild.__module__}): '
                                       f'{ie.detail}',
                                traceback=True)

    def create_guilds(self, bulk_data: List[Guild.__dict__]) -> Tuple[int, Sequence[Guild]]:
        try:
            logger.info('Attempting to create guilds.')

            guilds: Sequence[Guild] = bulk_create_guilds(self.db, bulk_data)
            logger.info('Guilds created')

            return 200, guilds
        except TypeError as te:
            logger.error(f'bulk_data contained incorrect data: {bulk_data}')
            logger.exception(te)

            raise HTTPException(500, detail=f'bulk_data contained invalid data: {bulk_data}')

    def guild(self, guild_id: Snowflake, name: str) -> Tuple[int, Guild]:
        logger.info(f'Finding or creating guild {name}.')
        try:
            guild: Tuple[Guild, bool] = get_or_create_one(self.db, Guild, guild_id=guild_id, name=name)

            return 200, guild[0]
        except TypeError as te:
            logger.error(f'TypeError while attempting to get or create {name} ({guild_id}).')
            logger.exception(f'{get_or_create_one.__module__} received incorrect arguments:\n\n{__file__}',
                             guild_id)
            logger.exception(te, guild_id)

            raise HTTPException(status_code=500, detail=f'Incorrect arguments received: '
                                                        f'{"guild_id": {guild_id}, "name": {name}}', traceback=True)

        except IntegrityError as ie:
            logger.error(f'Integral error while creating guild {name} ({guild_id}).')
            logger.exception(ie, guild_id)

            raise HTTPException(
                status_code=409,
                detail=f'{rel(__file__)}.{get_or_create_one.__name__} ({get_or_create_one.__module__}): {ie.detail}',
                traceback=True
            )

    def guilds(self):
        logger.info('Fetching all guilds.')

        return get_all(self.db, Guild)

    def member(
            self,
            guild_id: Snowflake,
            guild_name: str,
            member_id: Snowflake,
            username: str,
            discriminator: Optional[Discriminator] = None,
            nickname: Optional[str] = '',
    ) -> MemberShard:
        logger.info(f'Creating MemberShard for {username} in guild {guild_name} ({guild_id}).')
        logger.info(f'Searching for guild {guild_id}...')

        try:
            guild: Tuple[Guild, bool] = get_or_create_one(
                self.db, Guild, guild_id=guild_id, guild_name=guild_name
            )

            if guild[1] is False:
                logger.info(f'Guild {guild[0].guild_id} found as {guild[0].name}.')
            else:
                logger.warning(f'Guild {guild[0].name}({guild[0].guild_id}) was not in the db and was created.')

            new_member: Tuple[MemberShard, bool] = get_or_create_one(
                self.db,
                MemberShard,
                member_id=member_id,
                username=username,
                discriminator=discriminator,
                nickname=nickname,
            )

            if new_member[1]:
                logger.info(f'User {new_member[0].id} created, attaching to guild {guild[0].name}.')

                guild[0].members.append(new_member[0])
                self.db.add(guild)
                self.db.commit()

                logger.info(f'MemberShard #{new_member[0].id} successfully added to guild.')

                return new_member[0]
            elif not new_member[1]:
                logger.info('Member already exists and wasn\'t created again.')

                return new_member[0]
        except TypeError:
            logger.error(f'TypeError while attempting to add to {Guild.__qualname__}.')
            logger.exception(
                f'{self.__module__} received incorrect arguments:\n\n{__file__}',
                stack_info=True,
            )

            raise HTTPException(status_code=500, detail=f'Incorrect arguments received.', traceback=True)
        except IntegrityError as ie:
            logger.exception(
                f'{rel(__file__)}.{get_or_create_one.__name__}:' f' {ie.detail}', stack_info=True
            )

            raise HTTPException(status_code=500,
                                detail=f'{rel(__file__)}.{self.member.__name__} ({self.__module__}): {ie.detail}',
                                traceback=True)

    def members(self, guild_id: Snowflake):
        try:
            return get_all(self.db, MemberShard, guild_id)
        except NoResultFound as nrf:
            logger.error(f'No members for {guild_id} found.', guild_id)
            logger.exception(nrf, guild_id)

            raise HTTPException(status_code=404, detail=f'No members found for {guild_id}.')

    def update_guild(self, guild_id: Snowflake, **kwargs) -> Tuple[int, Guild]:
        try:
            logger.info(f'attempting to update guild ID {guild_id}...')

            upd: ReturningUpdate[Tuple[Guild]] = (
                update(Guild)
                .where(Guild.guild_id == guild_id)
                .values(**kwargs)
                .returning(Guild)
            )
            guild: Guild = self.db.execute(upd).scalars().unique().one()
            self.db.commit()
            logger.info('Guild updated.')

            return 200, guild

        except NoResultFound as nrf:
            logger.error('Guild is not created.', guild_id)
            logger.exception(nrf, guild_id)

        except KeyError as ke:
            logger.error(f'Incorrect kwargs provided:\n\n{kwargs}', guild_id)
            logger.exception(ke, guild_id)

    def update_member_shard(self, member_id: Snowflake, guild: Type[Guild], **kwargs) -> MemberShard:
        try:
            logger.info(f'attempting to update member_shard ID {member_id}...')

            upd: ReturningUpdate[Tuple[MemberShard]] = (
                update(MemberShard)
                .where(and_(MemberShard.guild_id == guild.guild_id, MemberShard.member_id == member_id))
                .values(**kwargs)
                .returning(MemberShard)
            )
            res = self.db.execute(upd).scalars().one()

            logger.info(f'Member {res.id} updated.')

            return res

        except NoResultFound:
            logger.error(f'Cannot find member {member_id}.')

    def delete_guild(self, guild_id: Snowflake) -> Guild | None:
        try:
            logger.info(f'Attempting to delete guild ID {guild_id}...')

            guild: Guild | None = self.db.execute(select(Guild).where(Guild.guild_id == guild_id)).unique().scalar_one()

            logger.info(f'Guild {guild.id} found. Deleting...')

            self.db.delete(guild)
            self.db.commit()

            return guild

        except NoResultFound as nrf:
            logger.error(f'Cannot find guild {guild_id}.', extra={'guild_id': guild_id})
            logger.exception(nrf, stack_info=True, exc_info=True, extra={'guild_id': guild_id})
            raise HTTPException(status_code=404, detail=f'Could not find guild {guild_id}.', traceback=True)

    def delete_member_shard(self, guild_id: Snowflake, member_id: Snowflake) -> MemberShard | None:
        try:
            logger.info('Attempting to delete member....')
            member_shard: MemberShard = self.db.execute(
                select(MemberShard).where(
                    and_(Guild.guild_id == guild_id, MemberShard.member_id == member_id)
                )
            ).unique().scalar_one()

            if member_shard is not None:
                logger.info(f'member_shard {member_shard.id} found. Deleting...')

            self.db.delete(member_shard)
            self.db.commit()

            return member_shard
        except NoResultFound as nrf:
            logger.error(f'Cannot find member {member_id}.', guild_id)
            logger.exception(nrf, guild_id)

    def prune(self, guild_id: Snowflake) -> List[Type[MemberShard]]:
        """
        Prunes members from a guild, without deleting the guild.\n

        Params:
        guild_id: strawberry.ID
            A strawberry.ID serialized int representing the Discord Server.id.
        """

        try:
            logger.info('Getting all member_shards that belong to guild...')
            member_shards: List[Type[MemberShard]] = (
                self.db.query(MemberShard).filter_by(guild_id=guild_id).all()
            )

            if len(member_shards) > 0:
                logger.info(f'Found {len(member_shards)} member_shards.')

            self.db.delete(member_shards)
            self.db.commit()

            return member_shards

        except NoResultFound as nrf:
            logger.error('No members to delete. If there are supposed to be members, check to see if they exist.',
                         guild_id)
            logger.exception(nrf, guild_id)
