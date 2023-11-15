from datetime import datetime
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from arrow import get, now
from arrow.arrow import Arrow

from ..config import sql


class Member(sql.Model):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    discriminator: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    member_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    nickname: Mapped[str] = mapped_column(String, server_default=f"{username}")
    admin_access: Mapped[bool] = mapped_column(Boolean, default=False)
    last_activity: Mapped[str] = mapped_column(String, server_default="None")
    last_active_server: Mapped[int] = mapped_column(BigInteger, default=0)
    last_active_channel: Mapped[int] = mapped_column(BigInteger, default=0)
    last_active_ts: Mapped[Arrow] = mapped_column(
        DateTime(timezone=True), default=get(datetime(1970, 1, 1, 0, 0)).datetime
    )
    idle_times: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[])
    # Instant avg like an instant MPG in the car.
    avg_idle_time: Mapped[int] = mapped_column(Integer, default=0)
    recent_avgs: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=[])
    # Overall Discord status. Not representative of individual servers.
    status: Mapped[str] = mapped_column(String, nullable=False, server_default="new")
    date_added: Mapped[Arrow] = mapped_column(sql.DateTime(timezone=True), default=now("US/Central").datetime)

    def __repr__(self):
        return (
            f"<Member (id = {self.id}, username = {self.username}, user_tag = {self.discriminator}"
            f"member_id = {self.member_id}, last_activity = {self.last_activity}, "
            f"last_active_server = {self.last_active_server}, last_active_channel = "
            f"{self.last_active_channel} last_active_ts = {self.last_active_ts.isoformat()}), "
            f"idle_times = {self.idle_times}, avg_idle_time = {self.avg_idle_time}, "
            f"recent_avgs = {self.recent_avgs}, status = {self.status}, date_added = "
            f"{self.date_added}>"
        )

    def as_dict(self):
        member_dict = {c.name: getattr(self, c.name) for c in self.__table__.mapped_columns}  # type: ignore
        member_dict["last_activity_ts"] = member_dict["last_activity_ts"].isoformat()
        member_dict["date_added"] = member_dict["date_added"].isoformat()

        return member_dict

    def update(self, new_timestamp):
        self.last_active_ts = new_timestamp