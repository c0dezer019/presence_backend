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
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

# Internal modules
from app.database import session
from app.database.models import BaseModel
from app.utils.logging import Logger

logger = Logger(__file__, __name__)


class MemberShard(BaseModel):
    __tablename__ = "member_shards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    snowflake: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guilds.id"))
    guild = relationship("Guild", back_populates="members")
    admin_access: Mapped[bool] = mapped_column(Boolean, default=False)
    flags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    last_act: Mapped[str] = mapped_column(String, nullable=True)
    last_act_server: Mapped[int] = mapped_column(BigInteger, nullable=True)
    last_act_ch: Mapped[int] = mapped_column(BigInteger, nullable=True)
    last_act_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    times_idle: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[])
    # Instant average like an instant MPG in the car.
    avg_idle_time: Mapped[int] = mapped_column(Integer, nullable=True)
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
        UniqueConstraint("snowflake", "guild_id", name="uq_snowflake_guild"),
    )

    @classmethod
    def bulk_create(cls: Type[MemberShard], session: Session, bulk_data: list[MemberShard]) -> Sequence[MemberShard]:
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

        data_dicts = list({d["snowflake"]: d for d in bulk_data}.values())

        stmt = insert(cls).values(data_dicts)
        conflict_stmt = stmt.on_conflict_do_update(
            constraint="uq_snowflake_guild",
            set_={
                c.name: getattr(stmt.excluded, c.name)
                for c in cls.__table__.columns
                if c.name not in ("id", "snowflake", "guild_id")
            },
        ).returning(cls)

        _cls: Sequence[MemberShard] = session.execute(conflict_stmt).unique().scalars().all()
        session.commit()

        return _cls

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
            return []

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
            f"<Member (id = {self.id}, name = {self.name}, "
            f"member_id = {self.snowflake}, guild = {self.guild}, last_activity = {self.last_act}, "
            f"last_active_server = {self.last_act_server}, last_active_channel = "
            f"{self.last_act_ch} last_active_ts = {self.last_act_ts.isoformat() if self.last_act_ts is not None else 'None'}), "
            f"idle_times = {self.times_idle}, average_idle_time = {self.avg_idle_time}, "
            f"recent_averages = {self.prev_avgs}, status = {self.status}, date_added = "
            f"{self.date_added}>"
        )

    def as_dict(self):
        member_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore
        member_dict["last_active_ts"] = member_dict["last_active_ts"].isoformat()
        member_dict["date_added"] = member_dict["date_added"].isoformat()

        return member_dict

    def soft_reset(self):
        defaults = {
            "last_act": None,
            "last_act_ch": None,
            "last_act_ts": None,
            "times_idle": [],
            "avg_idle_time": None,
            "prev_avgs": [],
            "status": "reset",
        }

        member = (
            update(MemberShard).filter_by(guild_id=self.guild_id).values(**defaults)
        )

        session.execute(member)
