# Internal modules
from __future__ import annotations

import logging
# External modules
from typing import List, Optional, Type, Tuple

from fastapi import HTTPException
from sqlalchemy import update, select, and_
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import ReturningUpdate

# Internal modules
from app.database.models import Guild, MemberShard
from app.database.utils import get_or_create_one, get_all
from utils import rel
from utils.types import Discriminator, Snowflake


class Resolver:
    def __init__(self, session: Session):
        self.db = session

    def guild(self, guild_id: Snowflake, name: str) -> Guild:
        logging.info(f'Finding or creating guild {name}.')
        guild: Tuple[Guild, bool] = get_or_create_one(self.db, Guild, guild_id=guild_id, name=name)

        return guild[0]

    def guilds(self):
        logging.info('Fetching all guilds.')

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
        logging.info(f'Creating MemberShard for {username} in guild {guild_name} ({guild_id}).')
        logging.info(f'Searching for guild {guild_id}...')

        try:
            guild: Tuple[Guild, bool] = get_or_create_one(
                self.db, Guild, guild_id=guild_id, guild_name=guild_name
            )

            if guild[1] is False:
                logging.info(f'Guild {guild[0].guild_id} found as {guild[0].name}.')
            else:
                logging.warning(
                    f'Guild {guild[0].name}({guild[0].guild_id}) was not in the db and was created.'
                )

            new_member: Tuple[MemberShard, bool] = get_or_create_one(
                self.db,
                MemberShard,
                member_id=member_id,
                username=username,
                discriminator=discriminator,
                nickname=nickname,
            )

            if new_member[1]:
                logging.info(f'User {new_member[0].id} created, attaching to guild {guild[0].name}.')

                guild[0].members.append(new_member[0])
                self.db.add(guild)
                self.db.commit()

                logging.info(f'MemberShard #{new_member[0].id} successfully added to guild.')

                return new_member[0]
            elif not new_member[1]:
                logging.info('Member already exists and wasn\'t created again.')

                return new_member[0]
        except TypeError:
            logging.error(f'TypeError while attempting to add to {Guild.__qualname__}.')
            logging.exception(
                f'{self.__module__} received incorrect arguments:\n\n{__file__}',
                stack_info=True,
            )

            raise HTTPException(status_code=500, detail=f'Incorrect arguments received.', traceback=True)
        except IntegrityError as ie:
            logging.exception(
                f'{rel(__file__)}.{get_or_create_one.__name__}:' f' {ie.detail}', stack_info=True
            )

            raise HTTPException(status_code=500,
                                detail=f'{rel(__file__)}.{self.member.__name__} ({self.__module__}): {ie.detail}',
                                traceback=True)

    def members(self, guild_id: Snowflake):
        try:
            return get_all(self.db, MemberShard, guild_id)
        except NoResultFound:
            logging.critical(f'No members for {guild_id} found.')

            raise HTTPException(status_code=404, detail=f'No members found for {guild_id}.')

    def update_guild(self, guild_id: Snowflake, c_name: str, **kwargs) -> Guild:
        try:
            logging.info(f'attempting to update guild ID {guild_id}...')

            upd: ReturningUpdate[Tuple[Guild]] = (
                update(Guild)
                .where(and_(Guild.guild_id == guild_id, Guild.name == c_name))
                .values(**kwargs)
                .returning(Guild)
            )
            res = self.db.execute(upd).scalars().one()
            logging.info('Guild updated.')

            return res

        except NoResultFound:
            logging.critical('Guild was not initialized, initializing now...')

            self.guild(guild_id, c_name, **kwargs)

        except KeyError:
            logging.critical(f'{self.__module__}.{rel(__file__)} Incorrect kwargs provided:\n\n{kwargs}',
                             stack_info=True)

    def update_member_shard(
            self, member_id: Snowflake, guild: Type[Guild], **kwargs
    ) -> MemberShard:
        try:
            logging.info(f'attempting to update member_shard ID {member_id}...')

            upd: ReturningUpdate[Tuple[MemberShard]] = (
                update(MemberShard)
                .where(and_(MemberShard.guild_id == guild.guild_id, MemberShard.member_id == member_id))
                .values(**kwargs)
                .returning(MemberShard)
            )
            res = self.db.execute(upd).scalars().one()

            logging.info(f'Member {res.id} updated.')

            return res

        except NoResultFound:
            logging.error(f'Cannot find member {member_id}.')

    def delete_guild(self, guild_id: Snowflake) -> Guild | None:
        try:
            logging.info(f'Attempting to delete guild ID {guild_id}...')

            guild: Guild | None = self.db.execute(
                select(Guild).where(Guild.guild_id == guild_id)
            ).scalar_one()

            logging.info(f'Guild {guild.id} found. Deleting...')

            self.db.delete(guild)
            self.db.commit()

            return guild

        except NoResultFound:
            logging.error('Cannot find guild.')
            raise NoResultFound

    def delete_member_shard(self, guild_id: Snowflake, member_id: Snowflake) -> MemberShard | None:
        try:
            logging.info('Attempting to delete member....')
            member_shard: MemberShard = self.db.execute(
                select(MemberShard).where(
                    and_(Guild.guild_id == guild_id, MemberShard.member_id == member_id)
                )
            ).unique().scalar_one()

            if member_shard is not None:
                logging.info(f'member_shard {member_shard.id} found. Deleting...')

            self.db.delete(member_shard)
            self.db.commit()

            return member_shard
        except NoResultFound:
            logging.critical(f'Cannot find member {member_id}.')
            logging.exception('Cannot delete a non-existent member')

    def prune(self, guild_id: Snowflake) -> List[Type[MemberShard]]:
        """
        Prunes members from a guild, without deleting the guild.\n

        Params:
        guild_id: strawberry.ID
            A strawberry.ID serialized int representing the Discord Server.id.
        """

        try:
            logging.info('Getting all member_shards that belong to guild...')
            member_shards: List[Type[MemberShard]] = (
                self.db.query(MemberShard).filter_by(guild_id=guild_id).all()
            )

            if len(member_shards) > 0:
                logging.info(f'Found {len(member_shards)} member_shards.')

            self.db.delete(member_shards)
            self.db.commit()

            return member_shards

        except NoResultFound:
            logging.warning(
                'No members to delete. If there are supposed to be members, check to see if they exist.'
            )
            logging.warning(f'{__file__}')
