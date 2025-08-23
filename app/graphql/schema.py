# Internal Modules
from dataclasses import asdict
from datetime import datetime
from typing import Optional, NewType, Sequence, Tuple

# External modules
import strawberry
from fastapi import HTTPException

# Internal modules
from ..graphql.resolvers import resolve
from ..utils.logging import Logger
from ..database.models.guild import Guild as DBGuild

logger = Logger(__file__, __name__)


Snowflake = strawberry.scalar(
    NewType("Snowflake", strawberry.ID),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
Dict = strawberry.scalar(
    NewType("Dict", dict),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
Discriminator = strawberry.scalar(
    NewType("Discriminator", int),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)
Set = strawberry.scalar(
    NewType("Set", set),
    serialize=lambda v: v,
    parse_value=lambda v: v,
)


@strawberry.interface
class User:
    member_id: Snowflake
    username: Optional[str] = strawberry.UNSET
    discriminator: Optional[int] = strawberry.UNSET
    admin_access: Optional[bool] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET
    flags: Optional[list[str]] = strawberry.UNSET


@strawberry.type
class NewMember(User):
    member_id: Snowflake
    username: str
    discriminator: int
    nickname: Optional[str] = strawberry.UNSET
    admin_access: Optional[bool] = strawberry.UNSET
    flags: Optional[list[str]] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET


@strawberry.type
class Member(User):
    member_id: Snowflake
    username: Optional[str] = strawberry.UNSET
    discriminator: Optional[int] = strawberry.UNSET
    nickname: Optional[str] = strawberry.UNSET
    admin_access: Optional[bool] = strawberry.UNSET
    last_activity: Optional[str] = strawberry.UNSET
    last_active_server: Optional[Snowflake] = strawberry.UNSET
    last_active_channel: Optional[Snowflake] = strawberry.UNSET
    last_active_ts: Optional[datetime] = strawberry.UNSET
    idle_times: Optional[list[int]] = strawberry.UNSET
    average_idle_time: Optional[int] = strawberry.UNSET
    recent_averages: Optional[list[int]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET
    flags: Optional[list[str]] = strawberry.UNSET


@strawberry.type
class MemberResult:
    code: int
    error: Optional[str] = strawberry.UNSET
    member: Optional[Member | NewMember] = strawberry.UNSET


@strawberry.type
class MembersResult:
    code: int
    error: Optional[str] = strawberry.UNSET
    members: Optional[Set] = strawberry.UNSET


@strawberry.interface
class Server:
    guild_id: Snowflake
    name: Optional[str] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET
    settings: Optional[Dict] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET


@strawberry.type
class Guild(Server):
    guild_id: Snowflake
    name: Optional[str] = strawberry.UNSET
    last_activity: Optional[str] = strawberry.UNSET
    last_active_channel: Optional[Snowflake] = strawberry.UNSET
    last_active_ts: Optional[datetime] = strawberry.UNSET
    idle_times: Optional[list[int]] = strawberry.UNSET
    average_idle_time: Optional[int] = strawberry.UNSET
    recent_averages: Optional[list[int]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET
    settings: Optional[Dict] = strawberry.UNSET
    members: Optional[Set] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET


@strawberry.type
class GuildResult:
    code: int
    error: Optional[str] = strawberry.UNSET
    guild: Optional[Guild] = strawberry.UNSET


@strawberry.type
class GuildsResult:
    code: int
    error: Optional[str] = strawberry.UNSET
    guilds: Optional[Set] = strawberry.UNSET


@strawberry.type
class DeleteResult:
    code: int
    success_msg: Optional[str] = strawberry.UNSET
    error: Optional[str] = strawberry.UNSET


@strawberry.input
class GuildCreate:
    guild_id: Snowflake
    name: str


@strawberry.input
class GuildsCreate:
    guilds: Set


@strawberry.input
class GuildUpdate:
    name: Optional[str] = strawberry.UNSET
    last_activity: Optional[str] = strawberry.UNSET
    last_active_channel: Optional[Snowflake] = strawberry.UNSET
    last_active_ts: Optional[datetime] = strawberry.UNSET
    idle_times: Optional[list[int]] = strawberry.UNSET
    average_idle_time: Optional[int] = strawberry.UNSET
    recent_averages: Optional[list[int]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET
    settings: Optional[Dict] = strawberry.UNSET
    members: Optional[Set] = strawberry.UNSET


@strawberry.input
class MemberCreate:
    member_id: Snowflake
    username: str
    discriminator: int
    nickname: Optional[str] = strawberry.UNSET
    flags: Optional[list[str]] = strawberry.UNSET


@strawberry.input
class MemberUpdate:
    nickname: Optional[str] = strawberry.UNSET
    username: Optional[str] = strawberry.UNSET
    discriminator: Optional[int] = strawberry.UNSET
    admin_access: Optional[bool] = strawberry.UNSET
    last_activity: Optional[str] = strawberry.UNSET
    last_active_server: Optional[Snowflake] = strawberry.UNSET
    last_active_channel: Optional[Snowflake] = strawberry.UNSET
    last_active_ts: Optional[datetime] = strawberry.UNSET
    idle_times: Optional[list[int]] = strawberry.UNSET
    average_idle_time: Optional[int] = strawberry.UNSET
    recent_averages: Optional[list[int]] = strawberry.UNSET
    flags: Optional[list[str]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET


@strawberry.type
class GuildMutations:
    @strawberry.mutation
    def create_guild(self, _input: GuildCreate) -> GuildResult:
        try:
            guild: Tuple[int, DBGuild] = resolve.create_guild(
                _input.guild_id, _input.name
            )

            return GuildResult(code=guild[0], guild=guild[1])

        except HTTPException as http_e:
            return GuildResult(code=http_e.status_code, error=http_e.detail)

    @strawberry.mutation
    def create_guilds(self, bulk_data: GuildsCreate) -> GuildsResult:
        try:
            guilds: Tuple[int, Sequence[DBGuild]] = resolve.create_guilds(bulk_data)

            return GuildsResult(code=guilds[0], guilds=guilds[1])

        except HTTPException as http_e:
            return GuildsResult(code=http_e.status_code, error=http_e.detail)

    @strawberry.mutation
    def update_guild(self, guild_id: int, _input: GuildUpdate) -> GuildResult:
        _input_dict = asdict(_input)
        try:
            updated: Tuple[int, DBGuild | None] = resolve.update_guild(
                guild_id, **_input_dict
            )

            return GuildResult(code=updated[0], guild=updated[1])

        except HTTPException as http_e:
            return GuildResult(
                code=http_e.status_code,
                error=f"Cannot update guild {guild_id}: {http_e.detail}",
            )

    @strawberry.mutation
    def reset_guild(self, guild_id: Snowflake) -> GuildResult:
        try:
            guild = resolve.reset_guild(blame=guild_id)

            return GuildResult(
                code=200,
                guild=guild
            )

        except HTTPException as http_e:
            return GuildResult(
                code=http_e.status_code,
                error=f"Cannot reset guild {guild_id}: {str(http_e.detail)}",
            )

    @strawberry.mutation
    def delete_guild(self, guild_id: Snowflake) -> DeleteResult:
        try:
            resolve.delete_guild(guild_id)

            return DeleteResult(
                code=200, success_msg=f"{guild_id} successfully deleted."
            )
        except HTTPException as http_e:
            return DeleteResult(code=http_e.status_code, error=http_e.detail)


@strawberry.type
class MemberMutations:
    @strawberry.mutation
    def create_member(
        self,
        _input: MemberCreate,
        guild_id: Snowflake,
        guild_name: str,
        nickname: Optional[str] = None,
    ) -> MemberResult:
        try:
            resolve.member(
                guild_id,
                guild_name,
                _input.member_id,
                _input.username,
                _input.discriminator,
                nickname,
            )

            return MemberResult(
                code=200,
                member=NewMember(
                    member_id=Snowflake(_input.member_id),
                    discriminator=_input.discriminator,
                    username=_input.username,
                    nickname=_input.nickname,
                ),
            )
        except HTTPException as http_e:
            return MemberResult(
                code=500, error=f"{_input.member_id} cannot be created: {http_e.detail}"
            )

    @strawberry.mutation
    def update_member(
        self, member_id: Snowflake, guild_id: Snowflake, _input: MemberUpdate
    ) -> MemberResult:
        """
        Updates a member_shard row.

        :param member_id: Discord user ID.

        :param guild_id: Discord server ID.

        :param _input: object containing data to update.

        :return: An instance of MemberResult.
        """

        _input_dict = asdict(_input)

        try:
            resolve.update_member_shard(member_id, guild_id, **_input_dict)

            return MemberResult(
                code=200,
                member=Member(
                    member_id=Snowflake(str(member_id)),
                    **_input_dict,
                ),
            )
        except HTTPException as http_e:
            return MemberResult(code=http_e.status_code, error=http_e.detail)

    @strawberry.mutation
    def delete_member(self, guild_id: Snowflake, member_id: Snowflake) -> DeleteResult:
        try:
            resolve.delete_member_shard(guild_id, member_id)

            return DeleteResult(
                code=200, success_msg=f"{member_id} has been removed from {guild_id}"
            )
        except HTTPException as http_e:
            return DeleteResult(
                code=http_e.status_code,
                error=f"{member_id} could not be removed from {guild_id} do to an unknown error: {str(http_e.detail)}",
            )


@strawberry.type
class MemberQueries:
    @strawberry.field
    def member(
        self,
        guild_id: Snowflake,
        guild_name: str,
        member_id: Snowflake,
        username: str,
        discriminator: Discriminator,
        nickname: Optional[str] = None,
    ) -> MemberResult:
        try:
            member = resolve.member(
                guild_id, guild_name, member_id, username, discriminator, nickname
            )

            member_dict = asdict(member)

            return MemberResult(code=200, member=Member(**member_dict))

        except HTTPException as http_e:
            return MemberResult(
                code=http_e.status_code,
                error=f"Unable to find member {member_id}: {str(http_e)}",
            )

    @strawberry.field
    def members(self, guild_id: Snowflake) -> MembersResult:
        try:
            members = resolve.members(guild_id)

            return MembersResult(code=200, members=members)

        except HTTPException as http_e:
            return MembersResult(
                code=http_e.status_code,
                error=f"Something went wrong while fetching members for guild {guild_id}: "
                f"{str(http_e)}",
            )


@strawberry.type
class GuildQueries:
    @strawberry.field
    def guild(self, guild_id: Snowflake, name: str) -> GuildResult:
        _guild = resolve.guild(guild_id, name)

        return GuildResult(code=_guild[0], guild=_guild[1])

    @strawberry.field
    def guilds(self, caller: Snowflake) -> GuildsResult:
        _guilds = resolve.guilds(caller)

        return GuildsResult(code=200, guilds=_guilds)


@strawberry.type
class Query:
    @strawberry.field
    def member(self) -> MemberQueries:
        return MemberQueries()

    @strawberry.field
    def guild(self) -> GuildQueries:
        return GuildQueries()


@strawberry.type
class Mutation:
    @strawberry.field
    def guild(self) -> GuildMutations:
        return GuildMutations()

    @strawberry.field
    def member(self) -> MemberMutations:
        return MemberMutations()


schema = strawberry.Schema(query=Query, mutation=Mutation)
