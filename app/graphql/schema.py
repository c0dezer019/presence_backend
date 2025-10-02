# Internal Modules
# Standard modules
import json
from dataclasses import asdict
from datetime import datetime
from typing import NewType, Optional, Sequence

# Third party modules
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

# External modules
from strawberry import (
    ID,
    UNSET,
    Schema,
    field,
    input,
    interface,
    mutation,
    scalar,
    type,
)

# Internal modules
from app.database.models.member_shard import MemberShard

from ..database.models.guild import Guild as DBGuild
from ..graphql.resolvers import resolve
from ..utils.logging import Logger

logger = Logger(__file__, __name__)

_settings_default = {
    "auto_kick": False,
    "time_before_inactive": 2592000
}

Snowflake = scalar(
    NewType("Snowflake", ID),
    serialize=lambda v: str(v),
    parse_value=lambda v: int(v),
)

JSON = scalar(
    NewType("JSON", dict),
    serialize=lambda v: json.loads(v),
    parse_value=lambda v: json.dumps(v)
)


@interface
class User:
    member_id: Snowflake
    admin_access: Optional[bool] = UNSET
    date_added: Optional[datetime] = UNSET
    flags: Optional[list[str]] = UNSET


@type
class IdleStats:
    times_idle: list[int] = field(default_factory=list)
    prev_avgs: list[int] = field(default_factory=list)


@type
class LastAct:
    ch: Optional[Snowflake] = UNSET
    type: Optional[str] = UNSET
    ts: Optional[datetime] = UNSET


@type
class Member(User):
    member_id: Snowflake
    admin_access: Optional[bool] = UNSET
    last_act: LastAct
    idle_stats: IdleStats
    status: Optional[str] = UNSET
    date_added: Optional[datetime] = UNSET
    flags: Optional[list[str]] = UNSET


@type
class MemberResult:
    code: int
    success: bool
    created: Optional[bool] = UNSET
    errors: list[str] = field(default_factory=list)
    member: Optional[Member] = UNSET


@type
class MembersResult:
    code: int
    success: bool
    errors: list[str] = field(default_factory=list)
    members: Optional[Member] = field(default_factory=list)


@type
class Settings:
    auto_kick: bool = field(default=False)
    time_before_inactive: int = field(default=2592000)


@interface
class Server:
    guild_id: Snowflake
    status: Optional[str] = UNSET
    settings: Optional[JSON] = UNSET
    date_added: Optional[datetime] = UNSET


@type
class Guild(Server):
    guild_id: Snowflake
    last_act: LastAct
    idle_stats: IdleStats
    status: Optional[str] = UNSET
    settings: JSON = field(default_factory=_settings_default)
    members: list[Member] = field(default_factory=list)
    date_added: Optional[datetime] = UNSET


@type
class GuildResult:
    code: int
    success: bool
    created: Optional[bool] = UNSET
    errors: list[str] = field(default_factory=list)
    guild: Optional[Guild] = UNSET


@type
class GuildsResult:
    code: int
    success: bool
    errors: list[str] = field(default_factory=list)
    guilds: list[Guild] = field(default_factory=list)


@type
class DeleteResult:
    code: int
    success_msg: Optional[str] = UNSET
    errors: list[str] = field(default_factory=list)


@input
class GuildCreate:
    guild_id: Snowflake


@input
class GuildsCreate:
    guilds: list[GuildCreate]


@input
class ISettings:
    auto_kick: Optional[bool] = UNSET
    time_before_inactive: Optional[int] = UNSET


@input
class UpdateLastAct:
    ch: Optional[Snowflake] = UNSET
    type: str
    ts: datetime


@input
class UpdateIdleStats:
    times_idle: list[int]
    prev_avgs: list[int]


@input
class GuildUpdate:
    last_act: Optional[UpdateLastAct] = UNSET
    idle_stats: Optional[UpdateIdleStats] = UNSET
    status: Optional[str] = UNSET
    settings: Optional[JSON] = UNSET


@input
class MemberCreate:
    member_id: Snowflake
    flags: Optional[list[str]] = UNSET


@input
class MemberUpdate:
    admin_access: Optional[bool] = UNSET
    last_act: Optional[UpdateLastAct] = UNSET
    idle_stats: Optional[UpdateIdleStats] = UNSET
    flags: Optional[list[str]] = UNSET
    status: Optional[str] = UNSET


@type
class GuildMutations:
    @mutation
    def create_guilds(self, bulk_data: GuildsCreate) -> GuildsResult:
        try:
            _guilds: Sequence[DBGuild] = resolve.create_guilds(bulk_data)

            guilds = []

            for guild in _guilds:
                guilds.append(
                    Guild(
                        guild_id=Snowflake(guild.guild_id),
                        last_act=LastAct(),
                        idle_stats=IdleStats(),
                    )
                )

            return GuildsResult(code=200, success=True, guilds=guilds)

        except HTTPException as http_e:
            return GuildsResult(
                code=http_e.status_code, success=False, errors=[http_e.detail]
            )

    @mutation
    def update_guild(self, guild_id: int, _input: GuildUpdate) -> GuildResult:
        try:
            _input_dict = asdict(_input)
            _guild: DBGuild = resolve.update_guild(guild_id, **_input_dict)

            guild = Guild(
                guild_id=Snowflake(_guild.guild_id),
                last_act=LastAct(
                    ch=_guild.last_act_ch,
                    type=_guild.last_act,
                    ts=_guild.last_act_ts,
                ),
                idle_stats=IdleStats(
                    times_idle=_guild.times_idle,
                    prev_avgs=_guild.prev_avgs,
                ),
                settings=JSON(_guild.settings),
                date_added=_guild.date_added
            )

            return GuildResult(code=200, success=True, guild=guild)

        except HTTPException as http_e:
            return GuildResult(
                code=http_e.status_code,
                success=False,
                errors=[f"Cannot update guild {guild_id}: {http_e.detail}"],
            )

    @mutation
    def reset_guild(self, guild_id: Snowflake) -> GuildResult:
        try:
            res: tuple[int, bool] = resolve.reset_guild(blame=guild_id)

            return GuildResult(code=res[0], success=res[1])

        except HTTPException as http_e:
            return GuildResult(
                code=http_e.status_code,
                success=False,
                errors=[f"Cannot reset guild {guild_id}: {str(http_e.detail)}"],
            )

    @mutation
    def delete_guild(self, guild_id: Snowflake) -> DeleteResult:
        try:
            resolve.delete_guild(guild_id)

            return DeleteResult(
                code=200, success_msg=f"{guild_id} successfully deleted."
            )
        except HTTPException as http_e:
            return DeleteResult(code=http_e.status_code, errors=[http_e.detail])


@type
class MemberMutations:
    @mutation
    def update_member(
        self, member_id: Snowflake, guild_id: Snowflake, _input: MemberUpdate
    ) -> MemberResult:
        """
        Updates a member_shard row.

        :param snowflake: Discord user ID.

        :param snowflake: Discord server ID.

        :param _input: object containing data to update.

        :return: An instance of MemberResult.
        """

        _input_dict = asdict(_input)

        try:
            member: MemberShard = resolve.update_member_shard(member_id, guild_id, **_input_dict)

            return MemberResult(
                code=200,
                success=True,
                member=Member(
                    member_id=Snowflake(member.member_id),
                    admin_access=member.admin_access,
                    flags=member.flags,
                    last_act=LastAct(
                        ch=member.last_act_ch,
                        type=member.last_act,
                        ts=member.last_act_ts,
                    ),
                    idle_stats=IdleStats(
                        times_idle=member.times_idle,
                        prev_avgs=member.prev_avgs,
                    ),
                    date_added=member.date_added,
                ),
            )
        except HTTPException as http_e:
            return MemberResult(
                code=http_e.status_code, success=False, errors=[http_e.detail]
            )
        except NoResultFound as nrf:
            return MemberResult(
                code=500, success=False, errors=[nrf]
            )

    @mutation
    def delete_member(self, member_id: Snowflake, guild_id: Snowflake) -> DeleteResult:
        try:
            resolve.delete_member_shard(member_id, guild_id)

            return DeleteResult(
                code=200, success_msg=f"{member_id} has been removed from {guild_id}"
            )
        except HTTPException as http_e:
            return DeleteResult(
                code=http_e.status_code,
                errors=[
                    f"{member_id} could not be removed from {guild_id} do to an unknown error: {str(http_e.detail)}"
                ],
            )


@type
class MemberQueries:
    @field
    def member(
        self,
        member_id: Snowflake,
        guild_id: Snowflake,
    ) -> MemberResult:
        try:
            _member: tuple[MemberShard, bool] = resolve.member(guild_id, member_id)

            member = Member(
                member_id=Snowflake(_member[0].member_id),
                admin_access=_member[0].admin_access,
                flags=_member[0].flags,
                last_act=LastAct(
                    ch=_member[0].last_act_ch,
                    type=_member[0].last_act,
                    ts=_member[0].last_act_ts,
                ),
                idle_stats=IdleStats(
                    times_idle=_member[0].times_idle,
                    prev_avgs=_member[0].prev_avgs,
                ),
                date_added=_member[0].date_added,
            )

            return MemberResult(code=200, success=True, created=_member[1], member=member)

        except HTTPException as http_e:
            return MemberResult(
                code=http_e.status_code,
                success=False,
                errors=[f"Unable to find member {member_id}: {str(http_e)}"],
            )

    @field
    def members(self, guild_id: Snowflake) -> MembersResult:
        try:
            members = resolve.members(guild_id)

            return MembersResult(code=200, success=True, members=members)

        except HTTPException as http_e:
            return MembersResult(
                code=http_e.status_code,
                success=False,
                errors=[
                    f"Something went wrong while fetching members for guild {guild_id}: {str(http_e)}"
                ],
            )


@type
class GuildQueries:
    @field
    def guild(self, guild_id: Snowflake) -> GuildResult:
        try:
            guild_members: tuple[tuple[DBGuild, bool], Sequence[MemberShard]] = resolve.guild(guild_id)
            _guild: DBGuild = guild_members[0][0]

            members = []
            for member in guild_members[1]:
                members.append(
                    Member(
                        member_id=Snowflake(member.member_id),
                        admin_access=member.admin_access,
                        date_added=member.date_added,
                        flags=member.flags,
                        last_act=LastAct(
                            ch=member.last_act_ch,
                            type=member.last_act,
                            ts=member.last_act_ts,
                        ),
                        idle_stats=IdleStats(
                            times_idle=member.times_idle,
                            prev_avgs=member.prev_avgs,
                        ),
                    )
                )

            guild = Guild(
                guild_id=Snowflake(_guild.guild_id),
                status=_guild.status,
                settings=JSON(_guild.settings),
                date_added=_guild.date_added,
                last_act=LastAct(
                    ch=_guild.last_act_ch, type=_guild.last_act, ts=_guild.last_act_ts
                ),
                idle_stats=IdleStats(
                    times_idle=_guild.times_idle,
                    prev_avgs=_guild.prev_avgs,
                ),
                members=members,
            )

            return GuildResult(code=200, success=True, created=guild_members[0][1], guild=guild)
        except HTTPException as http_e:
            return GuildResult(
                code=http_e.status_code,
                success=False,
                errors=[f"Unable to find guild {guild_id}: {str(http_e.detail)}"],
            )

    @field
    def guilds(self) -> GuildsResult:
        try:
            _guilds: Sequence[DBGuild] = resolve.guilds()
            guilds: list[Guild] = []

            for guild in _guilds:
                members = []

                for member in guild.members:
                    members.append(
                        Member(
                            member_id=Snowflake(member.member_id),
                            admin_access=member.admin_access,
                            flags=member.flags,
                            status=member.status,
                            last_act=LastAct(
                                ch=member.last_act_ch,
                                ts=member.last_act_ts,
                                type=member.last_act,
                            ),
                            idle_stats=IdleStats(
                                times_idle=member.times_idle,
                                prev_avgs=member.prev_avgs,
                            ),
                            date_added=member.date_added,
                        )
                    )
                guilds.append(
                    Guild(
                        guild_id=Snowflake(guild.guild_id),
                        status=guild.status,
                        last_act=LastAct(
                            ch=guild.last_act_ch,
                            type=guild.last_act,
                            ts=guild.last_act_ts,
                        ),
                        idle_stats=IdleStats(
                            times_idle=guild.times_idle,
                            prev_avgs=guild.prev_avgs,
                        ),
                        settings=json.loads(guild.settings),
                        date_added=guild.date_added,
                        members=members,
                    )
                )

            return GuildsResult(code=200, success=True, guilds=guilds)
        except HTTPException as http_e:
            return GuildsResult(
                code=http_e.status_code,
                success=False,
                errors=[f"Unable to fetch guilds: {str(http_e.detail)}"],
            )


@type
class Query:
    @field
    def member(self) -> MemberQueries:
        return MemberQueries()

    @field
    def guild(self) -> GuildQueries:
        return GuildQueries()


@type
class Mutation:
    @field
    def guild(self) -> GuildMutations:
        return GuildMutations()

    @field
    def member(self) -> MemberMutations:
        return MemberMutations()


schema = Schema(query=Query, mutation=Mutation)
