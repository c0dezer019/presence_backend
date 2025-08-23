# Internal modules
from typing import List, Sequence, cast

# External modules
from sqlalchemy import insert
from sqlalchemy.orm import Session

# Internal modules
from app.database.models import Guild, MemberShard
from app.graphql.lib.types import Model, Snowflake
from app.utils.logging import Logger

__name__ = '__create__'

logger = Logger(__file__, __name__)


def create_one_guild(db: Session, guild_id: Snowflake, name: str, **kwargs: object) -> Guild:
    logger.info(f'Attempting to create {name} ({guild_id}).')
    new_guild: Model = Guild(guild_id=guild_id, name=name, **kwargs)

    db.add(new_guild)
    db.commit()

    return new_guild


def bulk_create_guilds(db: Session, bulk_data: List[Guild]) -> Sequence[Guild]:
    logger.info('Attempting to bulk create Guilds.\n\n')
    logger.info(f'{bulk_data}')

    transaction = insert(Guild).values(bulk_data).returning(Guild)
    guilds: Sequence[Guild] = db.execute(transaction).unique().scalars().all()
    db.commit()

    return guilds


def create_one_member(db: Session, guild_id: Snowflake, member_id: Snowflake, username: str):
    logger.info(f'Attempting to create {username} ({member_id}) in {guild_id}.', cast(str, guild_id))
    new_member: Model = MemberShard(guild_id=guild_id, member_id=member_id, username=username)

    db.add(new_member)
    db.commit()


def bulk_create_members(db: Session, bulk_data: List[MemberShard]):
    logger.info('Attempting to bulk create MemberShards.\n\n', cast(str, bulk_data[0].member_id))
    logger.info(f'{bulk_data}', cast(str, bulk_data[0].member_id))

    transaction = insert(MemberShard).values(bulk_data).returning(MemberShard)
    db.execute(transaction)
