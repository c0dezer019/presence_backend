# Future modules
from __future__ import annotations

# Standard modules
from datetime import datetime
from typing import Sequence, Type

# Third party modules
from arrow import now
from dateutil.tz import gettz
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    literal_column,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, Session, mapped_column

# Internal modules
from app.database import session
from app.database.models import BaseModel
from app.utils.logging import Logger

logger = Logger(__file__, __name__)


class MemberShard(BaseModel):
    __tablename__ = "member_shards"

    SNOWFLAKE_FIELD = "member_id"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    member_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    guild_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("guilds.id", ondelete="cascade")
    )
    admin_access: Mapped[bool] = mapped_column(Boolean, default=False)
    flags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    last_act: Mapped[str] = mapped_column(String, nullable=True)
    last_act_ch: Mapped[int] = mapped_column(BigInteger, nullable=True)
    last_act_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    times_idle: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[])
    # Instant average like an instant MPG in the car.
    prev_avgs: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), default=[], nullable=True
    )
    # Overall Discord status. Not representative of individual servers.
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="new")
    date_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=now(gettz("US/Central")).datetime.isoformat(),
        default=now(gettz("US/Central")).datetime,
    )

    __table_args__ = (
        UniqueConstraint("member_id", "guild_id", name="uq_member_guild"),
    )

    @classmethod
    def bulk_create(
        cls: Type[MemberShard], session: Session, bulk_data: list[MemberShard]
    ) -> Sequence[MemberShard]:
        logger.info(
            "Attempting to bulk create %s %ss:\n\n", len(bulk_data), cls.__name__
        )
        logger.info(
            "%s%s",
            bulk_data[:5],
            "\n... plus {} more".format(len(bulk_data) - 5)
            if len(bulk_data) - 5 > 0
            else "",
        )

        data_dicts = list({d["member_id"]: d for d in bulk_data}.values())

        stmt = insert(cls).values(data_dicts)
        conflict_stmt = stmt.on_conflict_do_update(
            constraint="uq_member_guild",
            set_={
                c.name: getattr(stmt.excluded, c.name)
                for c in cls.__table__.columns
                if c.name not in ("id", "member_id", "guild_id")
            },
        ).returning(cls, literal_column("xmax"))

        results = session.execute(conflict_stmt).all()
        session.commit()

        members: list[MemberShard] = []
        created_count = 0
        updated_count = 0

        for member, xmax in results:
            member.__created__ = xmax == 0
            if member.__created__:
                created_count += 1
            else:
                updated_count += 1

            members.append(member)

        logger.info(
            "%s %s created, %s updated.", created_count, cls.__name__, updated_count
        )

        return members

    @classmethod
    def get_all(cls: Type[MemberShard], guild_id: int) -> Sequence[MemberShard]:
        logger.info(f"Fetching all instances of {cls.__name__}.")

        all: Sequence[MemberShard] | None = None

        all = (
            session.scalars(select(cls).where(MemberShard.guild_id == guild_id))
            .unique()
            .all()
        )

        if not all:
            logger.error("Unable to find any %s's in guild %s.", cls.__name__, guild_id)
            return []

        logger.info("%s %ss found.", all.count, cls.__name__)

        return all

    def __required_fields__(self):
        nullable = set()

        for col in self.__table__.columns:
            if (
                not col.nullable
                and not col.server_default
                and not col.default
                and not col.primary_key
            ):
                nullable.add(col.name)

        return nullable

    def __repr__(self):
        return (
            f"<Member (id = {self.id}, member_id = {self.member_id}, "
            f"guild_id = {self.guild_id}, admin_access = {self.admin_access}, "
            f"flags = {self.flags}, last_act = {self.last_act}, "
            f"last_act_ch = {self.last_act_ch}, last_act_ts = "
            f"{self.last_act_ts.isoformat() if self.last_act_ts is not None else 'None'}, "
            f"times_idle = {self.times_idle}, prev_avgs = {self.prev_avgs}, "
            f"status = {self.status}, date_added = {self.date_added}>"
        )

    def as_dict(self):
        member_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore
        member_dict["last_act_ts"] = member_dict["last_act_ts"].isoformat()
        member_dict["date_added"] = member_dict["date_added"].isoformat()

        return member_dict

    def soft_reset(self):
        defaults = {
            "last_act": None,
            "last_act_ch": None,
            "last_act_ts": None,
            "times_idle": [],
            "prev_avgs": [],
            "status": "reset",
        }

        member = (
            update(MemberShard).filter_by(guild_id=self.guild_id).values(**defaults)
        )

        session.execute(member)
