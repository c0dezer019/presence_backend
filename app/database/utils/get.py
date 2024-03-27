# Internal modules
from typing import Type, Optional

# Third-party modules
from sqlalchemy import select, Sequence
from sqlalchemy.orm import Session

# Internal modules
from app.database.models import Guild, MemberShard
from app.graphql.lib.types import Snowflake, Model, Query
from app.utils.logging import Logger

__name__ = '__get__'

logger = Logger(__file__, __name__)


def get_all(
        db: Session, model: Type[Guild | MemberShard], guild_id: Optional[Snowflake] = None
) -> Sequence[Guild | MemberShard]:
    """
    Gets all rows for the provided model. If a MemberShard and a guild_id is passed, it will get all MemberShards for
    the specified guild. Otherwise, it will fetch all rows for the given Model.

    :param db: The db session

    :param model: MemberShard | Guild

    :param guild_id: Snowflake (int)

    :returns: A Sequence of Guild or MemberShard rows.
    """

    if guild_id and model.__qualname__ == 'MemberShard':
        logger.info(f'Getting all MemberShards of {guild_id}.', guild_id)

        _all: Sequence[Guild] = db.execute(select(model).filter_by(guild_id=guild_id)).scalars().unique().all()

    else:
        logger.info(f'Retrieving all rows of "{model.__tablename__}."')

        _all: Sequence[MemberShard | Guild] = db.execute(select(model)).scalars().unique().all()

    return _all


def get_or_create_one(db: Session, model: Type[Guild | MemberShard], **kwargs: object) -> Query:
    """
    Either returns a Guild|MemberShard row or creates it and then returns it.

    :param db: The database session to be used to create the rows.

    :param model: MemberShard|Guild model

    :param kwargs: The values to add or search rows with.

    :return: A tuple of either a Guild or MemberShard and a bool.
    """

    instance: Model = db.scalars(select(model).filter_by(**kwargs)).unique().one_or_none()

    if instance:
        logger.info(
            f'{instance} with ID {instance.guild_id if type(instance) is Guild else instance.member_id} found.',
            instance.guild_id
        )

        return instance, False
    else:
        logger.info('Not found, creating...', instance.guild_id)
        instance: Model = model(**kwargs)

        db.add(instance)
        db.commit()

        logger.info(
            f'{model.__qualname__} created with with ID '
            f'{instance.guild_id if type(instance) is Guild else instance.member_id}',
            instance.guild_id
        )

        return instance, True
