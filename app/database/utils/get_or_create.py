from __future__ import annotations

from typing import Any, Type

from sqlalchemy import Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import Guild, MemberShard


def get_or_create(db: Session, model, **kwargs) -> (tuple[Guild | Type[MemberShard], bool] |
                                                    tuple[Row[tuple[Any]], bool]):
    instance = db.query(model).filter_by(**kwargs).one_or_none()

    if instance:
        return instance, False
    else:
        try:
            instance = model(**kwargs)

            db.add(instance)
            db.commit()

        except TypeError as te:
            print(te)

        else:
            return instance, True
