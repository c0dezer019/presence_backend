# Internal modules
import logging
from typing import Type, Optional

# Third-party modules
from fastapi import HTTPException
from sqlalchemy import select, Sequence
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Internal modules
from app.database.models import Guild, MemberShard
from app.graphql.lib.types import Snowflake, Query, Model
from utils.logging import rel


def get_all(
    db: Session, model: Type[Guild | MemberShard], guild_id: Optional[Snowflake] = 0
) -> Sequence[Guild | MemberShard]:
    """
    Gets all rows for the provided model. If a MemberShard and a guild_id is passed,
    it will get all MemberShards for the specified guild.

    :param db: The db session

    :param model: MemberShard | Guild

    :param guild_id: Snowflake (int)

    :returns: A Sequence of Guild or MemberShard rows.
    """

    if guild_id and model.__qualname__ == 'MemberShard':
        _all: Sequence[Guild] = db.execute(
            select(model).filter_by(guild_id=guild_id)
        ).scalars().unique().all()
    else:
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

    try:
        instance: Model = db.scalars(select(model).filter_by(**kwargs)).unique().one_or_none()

        if instance:
            logging.info(
                f'{instance} with ID {instance.guild_id if type(instance) is Guild else instance.member_id} found.'
            )

            return instance, False
        else:
            logging.info('Not found, creating...')
            instance: Guild | MemberShard = model(**kwargs)

            db.add(instance)
            db.commit()

            logging.info(
                f'{model.__qualname__} created with with ID '
                f'{instance.guild_id if type(instance) is Guild else instance.member_id}'
            )

            return instance, True

    except TypeError:
        logging.error(f'TypeError while attempting to get or create {model.__qualname__}.')
        logging.exception(
            f'{get_or_create_one.__module__} received incorrect arguments:\n\n{__file__}',
            stack_info=True,
        )

        raise HTTPException(status_code=500, detail=f'Incorrect arguments received: {kwargs}.', traceback=True)

    except IntegrityError as ie:
        logging.exception(
            f'{rel(__file__)}.{get_or_create_one.__name__}:' f' {ie.detail}', stack_info=True
        )

        raise HTTPException(status_code=500,
                            detail=f'{rel(__file__)}.{get_or_create_one.__name__} ({get_or_create_one.__module__}): '
                                   f'{ie.detail}',
                            traceback=True)
