# Internal modules
from typing import Optional

# Third party modules
from strawberry import ID
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

# Internal modules
from app.database import session
from app.database.models import Guild, MemberShard


class Resolver:
    def _update_entity(self, entity: Guild | MemberShard, data: dict):
        for k, v in data.items():
            try:
                entity.__setattr__(k, v)
                self.db.commit()
            except (NameError, AttributeError):
                pass

    def __init__(self):
        self.db = session

    def create_guild(self, **kwargs) -> Guild:
        guild: Guild = Guild(**kwargs)

        self.db.add(guild)

        try:
            self.db.commit()
        except IntegrityError:
            print("Already exists.")

        return guild

    def updater(
        self, guild_id: ID, member_id: Optional[ID], **kwargs
    ) -> Guild | MemberShard:
        guild: Guild = self.db.execute(
            select(Guild).filter_by(guild_id=guild_id)
        ).scalar_one()
        member: MemberShard | None = (
            self.db.execute(
                select(MemberShard).filter_by(guild_id=guild_id)
            ).scalar_one()
            if member_id
            else None
        )

        if member is None:
            self._update_entity(guild, kwargs)

            return guild
        else:
            self._update_entity(member, kwargs)

            return member

    def delete_entity(
        self, guild_id: ID, member_id: Optional[ID]
    ) -> Guild | MemberShard | None:
        entity: MemberShard | Guild | None = (
            self.db.query(Guild if not member_id else MemberShard)
            .filter_by(guild_id=guild_id)
            .first()
        )

        try:
            self.db.delete(entity)
            self.db.commit()
        except UnmappedInstanceError:
            pass

        return entity

    def prune(self, guild_id: ID):
        member_shard_table = MemberShard.__table__

        stmt = delete(MemberShard).where(
            member_shard_table.c.guild_id == guild_id
        )
        self.db.execute(stmt)
