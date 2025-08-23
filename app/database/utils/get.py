# Internal modules
from typing import Type, Optional, List, Sequence, cast

# Third-party modules
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

# Internal modules
from app.database.models import Guild
from app.database.models.member_shard import MemberShard
from app.graphql.lib.types import Snowflake, Model, Query
from app.utils.logging import Logger

__name__ = "__get__"

logger = Logger(__file__, __name__)


def get_all(
    db: Session,
    model: type[MemberShard] | type[Guild],
    blame: Snowflake,
    guild_id: Optional[Snowflake] = None,
) -> Sequence[Guild | MemberShard]:
    """
    Gets all rows for the provided model. If a MemberShard and a guild_id is passed, it will get all MemberShards for
    the specified guild. Otherwise, it will fetch all rows for the given Model.

    :param db: The db session
    :param model: MemberShard | Guild
    :param blame: Snowflakes that called the function.
    :param guild_id: Snowflake (int)

    :returns: A Sequence of Guild or MemberShard rows.
    """

    if guild_id and model.__qualname__ == "MemberShard":
        logger.info(f"Getting all MemberShards of {guild_id}.", cast(str, blame))

        smtp: Select = select(model).filter_by(guild_id=guild_id)

        return db.execute(smtp).scalars().unique().all()

    else:
        logger.info(
            f'Retrieving all rows of "{model.__tablename__}."', cast(str, blame)
        )

        smtp: Select = select(model)

        return db.execute(smtp).scalars().unique().all()


def get_or_create_one(
    db: Session, model: Type[Model], blame: str, **kwargs: object
) -> Query:
    """
    Either returns a Guild|MemberShard row or creates it and then returns it.

    :param db: The database session to be used to create the rows.
    :param model: MemberShard|Guild model
    :param blame: Snowflakes that initiated the function.
    :param kwargs: The values to add or search rows with.

    :return: A tuple of either a Guild or MemberShard and a bool.
    """

    instance: Model | None = (
        db.scalars(select(model).filter_by(**kwargs)).unique().one_or_none()
    )

    if instance:
        logger.info(
            f"{instance} with ID {instance.guild_id if type(instance) is Guild else instance.member_id if type(instance) is MemberShard else 'None'} found.",
            blame,
        )

        return instance, False
    else:
        logger.info("Not found, creating...", blame)
        instance = model(**kwargs)

        db.add(instance)
        db.commit()

        logger.info(
            f"{model.__qualname__} created with ID "
            f"{instance.guild_id if type(instance) is Guild else instance.member_id if type(instance) is MemberShard else 'None'} found.",
            blame,
        )

        return instance, True


def filtered(
    db: Session,
    model: Type[Model],
    blame: str,
    snowflakes: List[Snowflake],
    **kwargs,
) -> List[Model]:
    """
    :param db: The database session to be used to create the rows.
    :param model: MemberShard | Guild model.
    :param blame: Snowflake of entity that initiated the function (either will be DM or channel/guild).
    :param snowflakes: A list of snowflakes to be returned.

    :return: A Sequence of Guilds or MemberShards.
    """
    logger.info(f"Attempting to get {model.__qualname__}s:\n\n[{snowflakes}].", blame)

    id = None

    if model is Guild:
        id = model.guild_id
    elif model is MemberShard:
        id = model.member_id

    if id:
        sequence = (
            (db.execute(select(model).where(id.in_(snowflakes)).filter_by(**kwargs)))
            .unique()
            .scalars()
            .all()
        )
    else:
        raise UnboundLocalError()

    return [guild for guild in sequence]
