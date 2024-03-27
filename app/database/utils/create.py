# Internal modules
from typing import List

# External modules
from sqlalchemy import insert, Sequence
from sqlalchemy.orm import Session

# Internal modules
from app.database.models import Guild, MemberShard
from app.graphql.lib.types import Model, Snowflake
from app.utils.logging import Logger

__name__ = '__create__'

logger = Logger(__file__, __name__)


def create_one_guild(db: Session, guild_id: Snowflake, name: str, **kwargs: object):
    logger.info(f'Attempting to create {name} ({guild_id}).')
    new_guild: Model = Guild(guild_id=guild_id, name=name, **kwargs)

    db.add(new_guild)
    db.commit()


def bulk_create_guilds(db: Session, bulk_data: List[Guild.__dict__]) -> Sequence[Guild]:
    logger.info('Attempting to bulk create Guilds.\n\n')
    logger.info(f'{bulk_data}')

    transaction = insert(Guild).returning(Guild)
    guilds: Sequence[Guild] = db.execute(transaction, bulk_data).unique().scalars().all()
    db.commit()

    return guilds


def create_one_member(db: Session, guild_id: Snowflake, member_id: Snowflake, username: str):
    logger.info(f'Attempting to create {username} ({member_id}) in {guild_id}.', guild_id)
    new_member: Model = MemberShard(guild_id=guild_id, member_id=member_id, username=username)

    db.add(new_member)
    db.commit()


def bulk_create_members(db: Session, bulk_data: List[MemberShard.__dict__]):
    logger.info('Attempting to bulk create MemberShards.\n\n', bulk_data[0].guild_id)
    logger.info(f'{bulk_data}', bulk_data[0].guild_id)

    transaction = insert(MemberShard).values(bulk_data).returning(MemberShard)
    db.execute(transaction)
