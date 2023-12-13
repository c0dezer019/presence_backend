# Internal modules
from __future__ import annotations

import logging
from typing import List, Optional, Type

from fastapi import HTTPException
# Third party modules
from sqlalchemy import update, Update
from sqlalchemy.exc import NoResultFound

# Internal modules
from app.database import database
from app.database.models import Guild, MemberShard
from app.database.utils import get_or_create_one
from utils.types import Discriminator, Snowflake


class Resolver:
    def __init__(self):
        self.db = database

    def guild(self, guild_id: Snowflake, name: str) -> Guild:
        logging.info(f'Creating guild {name}.')
        guild: tuple[Guild, bool] = get_or_create_one(self.db.session, Guild, guild_id=guild_id, name=name)

        return guild[0]

    def member(self, guild_id: Snowflake, guild_name: str, member_id: Snowflake, username: str,
               discriminator: Discriminator, nickname: Optional[str] = None) -> MemberShard:
        logging.info(f'Creating MemberShard for {username} in guild {guild_name} '
                     f'({guild_id})')
        try:
            logging.info(f'Searching for guild {guild_name}...')
            guild: Guild | None = (self.db.session.query(Guild).where(Guild.guild_id == guild_id)
                                   .where(Guild.name == guild_name).first())

            if guild is not None:
                logging.info(f'Guild {guild.id} found as {guild.name}.')

            new_member: tuple[Guild | MemberShard, bool] = \
                get_or_create_one(self.db.session, MemberShard, member_id=member_id, username=username,
                                  discriminator=discriminator, nickname=nickname)

            if new_member[1]:
                logging.info(
                    f'User {new_member[0].id} created, attaching to guild {guild.name}.')

                guild.members.append(new_member[0])
                self.db.session.add(guild)
                self.db.session.commit()

                logging.info(f'MemberShard #{new_member[0].id} successfully added to guild.')

        except NoResultFound:
            logging.critical(f'Guild {guild_name} ({guild_id}) not found. Creating...')
            guild = self.guild(guild_id, guild_name)

            if guild in self.db:
                logging.info('Attempting to recreate member.')
                self.member(guild_id, guild_name, member_id, username, discriminator)
            else:
                logging.critical(f'Guild failed to be created. {__file__}: {self.guild.__name__}')
        else:
            logging.warning(f'Member already exists and wasn\'t created again.')

            return new_member[0]

    def update_guild(self, guild_id: Snowflake, c_name: str, **kwargs) -> Guild:
        try:
            logging.info(f'attempting to update guild ID {guild_id}...')

            upd = (update(Guild)
                   .where(Guild.guild_id == guild_id)
                   .where(Guild.name == c_name)
                   .values(**kwargs)
                   .returning(Guild))
            res = self.db.session.execute(upd).scalars().one()
            logging.info('Guild updated.')

            return res

        except NoResultFound:
            logging.critical('Guild was not initialized, initializing now...')

            self.guild(guild_id, c_name)
            logging.info('Attempting to update guild with data...')

            self.update_guild(guild_id, c_name, kwargs)

    def update_member_shard(self, member_id: Snowflake, guild_id: Snowflake, **kwargs) -> MemberShard:
        try:
            logging.info(f'attempting to update member_shard ID {member_id}...')

            upd: Update = (update(MemberShard).where(MemberShard.member_id == member_id)
                           .where(Guild.guild_id == guild_id)
                           .values(**kwargs)
                           .returning(MemberShard))
            res: MemberShard = self.db.session.execute(upd).scalars().one()

            logging.info(f'Member {res.id} updated.')

            return res
        except NoResultFound:
            logging.critical('Cannot find member.')
            logging.exception('Cannot update a non-existent member.')

            raise HTTPException(status_code=404)

    def delete_guild(self, guild_id: Snowflake) -> Guild | None:
        try:
            logging.info(f'Attempting to delete guild ID {guild_id}...')

            guild: Guild | None = self.db.session.query(Guild).filter_by(guild_id=guild_id).first()

            logging.info(f'Guild {guild.id} found. Deleting...')

            self.db.session.delete(guild)
            self.db.session.commit()

            return guild

        except NoResultFound:
            logging.critical('Cannot find guild.')
            logging.exception('Cannot delete a non-existing guild')

    def delete_member_shard(self, guild_id: Snowflake, member_id: Snowflake) -> MemberShard | None:
        try:
            logging.info("Attempting to delete member....")
            member_shard: Guild | None = (self.db.session.query(MemberShard)
                                          .filter(Guild.guild_id == guild_id, MemberShard.member_id == member_id)
                                          .first())

            if member_shard is not None:
                logging.info(f'member_shard {member_shard.id} found. Deleting...')

            self.db.session.delete(member_shard)
            self.db.session.commit()

            return member_shard
        except NoResultFound:
            logging.critical('Cannot find member.')
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
            member_shards: List[Type[MemberShard]] = self.db.query(MemberShard).filter_by(guild_id=guild_id).all()

            if len(member_shards) > 0:
                logging.info(f'Found {len(member_shards)} member_shards.')

            self.db.session.delete(member_shards)
            self.db.session.commit()

            return member_shards

        except NoResultFound:
            logging.warning('No members to delete. If there are supposed to be members, check to see if they exist.')
            logging.warning(f'{__file__}')
