# TODO: finish documentation

# Future modules
from __future__ import annotations

# Standard modules
import json
from datetime import datetime
from typing import Any, Optional, Sequence, Type

# Third party modules
from arrow import now
from dateutil.tz import gettz
from sqlalchemy import (
    ARRAY,
    BigInteger,
    DateTime,
    Integer,
    String,
    delete,
    literal_column,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import Mapped, WriteOnlyMapped, Session, mapped_column, relationship

# Internal modules
from app.database.models import BaseModel
from app.database.models.member_shard import MemberShard
from app.utils.logging import Logger

logger = Logger(__file__, __name__)


class Guild(BaseModel):
    __tablename__ = "guilds"

    _settings = {"auto_kick": False, "time_before_inactive": 2592000}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    last_act: Mapped[str] = mapped_column(String, nullable=True, default=None)
    last_act_ch: Mapped[int] = mapped_column(BigInteger, nullable=True, default=None)
    last_act_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    times_idle: Mapped[int] = mapped_column(ARRAY(Integer), nullable=True, default=[])
    prev_avgs: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[])
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="new")
    settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=json.dumps(_settings),
        server_default=json.dumps(_settings),
    )
    members: WriteOnlyMapped["MemberShard"] = relationship(
        "MemberShard", cascade="all,delete-orphan", passive_deletes=True
    )
    date_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=now(gettz("US/Central")).datetime.isoformat(),
        default=now(gettz("US/Central")).datetime,
    )

    @classmethod
    def bulk_create(
        cls: Type[Guild], session: Session, bulk_data: list[Guild]
    ) -> Sequence["Guild"]:
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

        data_dicts = list({d["guild_id"]: d for d in bulk_data}.values())

        stmt = insert(cls).values(data_dicts)
        conflict_stmt = stmt.on_conflict_do_update(
            index_elements=[cls.guild_id],
            set_={
                c.name: getattr(stmt.excluded, c.name)
                for c in cls.__table__.columns
                if c.name not in ("guild_id", "id")
            },
        ).returning(cls, literal_column("xmax"))

        logger.info("Creating or updating %s", cls.__name__)

        results = session.execute(conflict_stmt).all()
        session.commit()

        guilds: list[Guild] = []
        created_count = 0
        updated_count = 0

        for guild, xmax in results:
            guild.__created__ = xmax == 0
            if guild.__created__:
                created_count += 1
            else:
                updated_count += 1

            guilds.append(guild)

        logger.info(
            "%s %s created. %s updated.", created_count, cls.__name__, updated_count
        )

        return guilds

    def get_members(self, session: Session) -> Sequence[MemberShard]:
        members = session.scalars(self.members.select()).all()

        return members

    def prune(self, session: Session):
        cutoff = (
            now()
            .shift(seconds=-json.loads(self.settings)["time_before_inactive"])
            .isoformat()
        )

        session.execute(
            delete(MemberShard).filter(
                MemberShard.guild_id == self.id,
                MemberShard.last_act_ts < cutoff,
                MemberShard.status == "archived",
            )
        )
        session.commit()

    def add_member(self, session: Session, member: MemberShard):
        self.members.add(member)
        session.commit()

    def __required_fields__(self):
        nullable = set()

        for col in self.__table__.columns:
            if (
                not col.nullable
                and not col.server_default
                and not col.default
                and not col.primary_key
            ):
                nullable.add(col)

        return nullable

    def __repr__(self):
        return (
            f"<Guild (id = {self.id}, guild_id = {self.guild_id}, "
            f"last_activity = {self.last_act}, last_active_channel = {self.last_act_ch}, "
            f"last_active_ts = {self.last_act_ts}, idle_times = {self.times_idle}, "
            f"recent_averages = {self.prev_avgs}, status = {self.status}, "
            f"settings = {self.settings}, members = {self.members}, "
            f"date_added = {self.date_added})>"
        )

    def as_dict(self, session: Session):
        guild_dict = {
            c.name: getattr(self, c.name) for c in self.__table__.columns.values()
        }
        guild_dict["members"] = []

        for member in session.scalars(self.members.select()).all():
            member_dict = member.as_dict()
            guild_dict["members"].append(member_dict)

        return guild_dict

    def hard_reset(self, session):
        """
        WARNING: This is a hard reset and clears all users from a guild and resets all stats. Only to be used to fix database errors and all other measures fail.
        """
        members = (
            session.scalars(select(MemberShard).filter_by(guild_id=self.guild_id))
            .unique()
            .all()
        )

        defaults = {
            "last_act": None,
            "last_act_ch": None,
            "last_act_ts": None,
            "times_idle": [],
            "prev_avgs": [],
            "status": "reset",
        }
        guild = (
            update(Guild).where(Guild.guild_id == self.guild_id).values(**defaults)
        )

        for member in members:
            session.delete(member)

        session.execute(guild)
        session.commit()
        session.refresh(self)

    def soft_reset(self, session, member_id: Optional[int] = None):
        """
        Resets all data to default values to the day the bot joined the guild.

        When the bot joins the guild, the bot will measure activity based on last messages and if able, actions, of a Member. After the bot has configured, it will perform automoderation if that is set up, irregardless of how long the bot has been monitoring the activities. This function is necessary when the Guild admins do not want that to happen. Upon configuration, this function will run so that the bot starts with a fresh perspective, instead of a biased baseline.
        """

        defaults = {
            "last_act": None,
            "last_act_ch": None,
            "last_act_ts": None,
            "times_idle": [],
            "prev_avgs": [],
            "status": "reset",
        }

        members = (
            session.scalars(select(MemberShard).filter_by(guild_id=self.guild_id))
            .unique()
            .all()
        )
        guild_update = (
            update(Guild).where(Guild.guild_id == self.guild_id).values(**defaults)
        )
        session.execute(guild_update)

        for member in members:
            updated = (
                update(MemberShard)
                .where(
                    MemberShard.guild_id == self.guild_id
                    and MemberShard.member_id == member.member_id
                )
                .values(**defaults)
            )

            session.execute(updated)

        session.commit()
        session.refresh(self)
