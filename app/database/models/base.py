# Third party modules

# Standard modules
from typing import Any, Type, TypeVar

# Third party modules
from sqlalchemy import select
from sqlalchemy.orm import Session, declarative_base

# Internal modules
from app.utils.logging import Logger

Base = declarative_base()

T = TypeVar("T", bound="BaseModel")

logger = Logger(__file__, __name__)


class BaseModel(Base):
    __abstract__ = True

    # Name of the column that acts as this model's snowflake/identity field.
    # Subclasses override this since the actual column is named differently
    # per model (e.g. Guild.guild_id, MemberShard.member_id).
    SNOWFLAKE_FIELD: str = "snowflake"

    @classmethod
    def get_one(cls: Type[T], session: Session, snowflake: int) -> T | False:
        logger.info("Searching %s for ID %s.", cls.__name__, snowflake)

        one = session.scalar(
            select(cls).where(getattr(cls, cls.SNOWFLAKE_FIELD) == snowflake)
        )

        if not one:
            logger.info("%s %s not found.", cls.__name__, snowflake)
            return False

        logger.info(
            "%s %s(%s) found.",
            one.__class__.__name__,
            one.name,
            getattr(one, one.SNOWFLAKE_FIELD),
        )

        return one

    @classmethod
    def find_or_create(
        cls: Type[T], session: Session, defaults: dict[str, Any], **kwargs
    ) -> tuple[T, bool]:
        """
        Finds an instance by snowflake or creates it if not found.
        Returns (instance, created: bool).
        """

        missing = [
            col.name
            for col in cls.__table__.columns
            if col.name not in defaults.keys()
            and not col.default
            and not col.server_default
            and not col.nullable
            and not col.primary_key
        ]

        if missing:
            logger.info("%s missing required arguments: %s", cls.__name__, missing)
            raise TypeError(f"Defaults is missing the following arguments: {missing}")

        snowflake = defaults.get(cls.SNOWFLAKE_FIELD)

        logger.info("Checking to see if %s already exists.", cls.__name__)
        instance = cls.get_one(session, snowflake)

        if instance:
            logger.info("%s with ID %d found.", cls.__name__, snowflake)
            return instance, False

        logger.info("Not found, creating %s...", cls.__name__)

        instance = cls.create_one(session, defaults, **kwargs)

        logger.info("%s created with ID %d.", cls.__name__, snowflake)

        return instance, True

    @classmethod
    def create_one(
        cls: Type[T], session: Session, defaults: dict[str, Any], **kwargs
    ) -> T:
        missing = [
            col.name
            for col in cls.__table__.columns
            if col.name not in defaults.keys()
            and not col.default
            and not col.server_default
            and not col.nullable
            and not col.primary_key
        ]

        if missing:
            logger.error("%s is missing required arguments: %s", cls.__name__, missing)

            raise TypeError(f"Defaults is missing the following arguments: {missing}")

        logger.info(
            "Creating %s: %s (%s)",
            cls.__name__,
            defaults.get("name"),
            defaults.get(cls.SNOWFLAKE_FIELD),
        )

        add = {**defaults, **kwargs}

        _cls = cls(**add)

        session.add(_cls)
        session.commit()

        logger.info("%s created:\n\n%s", cls.__name__, _cls)

        return _cls
