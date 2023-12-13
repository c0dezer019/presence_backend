# Internal modules
from typing import Type
import logging

# Third-party modules
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Internal modules
from app.database.models import Guild, MemberShard
from utils.types import Model,  Query


def get_or_create_one(db: Session, model: Type[Guild | MemberShard], **kwargs) -> Query:
    instance: Model = db.query(model).filter_by(**kwargs).one_or_none()

    if instance:
        logging.info(
            f'{instance} with ID {instance.guild_id if type(instance) is Guild else instance.member_id} found.'
        )

        return instance, False
    else:
        try:
            logging.info('Not found, creating...')
            instance: Guild | MemberShard = model(**kwargs)

            db.add(instance)
            db.commit()

        except TypeError as te:
            logging.error(f'TypeError while attempting to get or create {model.__qualname__}:\n\n{te}')

        except IntegrityError:
            guild = get_or_create_one(db, model, kwargs)

            logging.error(
                f'Attempted to create a row with a duplicate id or discriminator while creating a {model.__qualname__}'
                f'\nID: {kwargs["guild_id" if "guild_id" in kwargs.keys() else "member_id"]}\n'
                f'Existing row found: {guild}'
            )

            raise HTTPException(status_code=400, detail='You cannot create another guild with a duplicate ID.')

        else:
            logging.info(
                f'{model.__qualname__} created with with ID '
                f'{instance.guild_id if type(instance) is Guild else instance.member_id}'
            )

            return instance, True
