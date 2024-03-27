# Internal Modules
from datetime import datetime
from typing import Optional, NewType, List, Tuple

# External modules
import strawberry
from fastapi import HTTPException
from sqlalchemy import Sequence

# Internal modules
from app.graphql.resolvers import resolve

Snowflake = strawberry.scalar(
    NewType("Snowflake", strawberry.ID), serialize=lambda v: v, parse_value=lambda v: v
)
Dict = strawberry.scalar(
    NewType("Dict", dict), serialize=lambda v: v, parse_value=lambda v: v
)
Discriminator = strawberry.scalar(
    NewType("Discriminator", int), serialize=lambda v: v, parse_value=lambda v: v
)
Set = strawberry.scalar(
    NewType("Set", set), serialize=lambda v: v, parse_value=lambda v: v
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
class Query:
    @strawberry.field
    def member(
            self,
            guild_id: Snowflake,
            guild_name: str,
            member_id: Snowflake,
            username: str,
            discriminator: Discriminator,
            nickname: Optional[str] = "",
    ) -> MemberResult:
        try:
            member = resolve.member(
                guild_id, guild_name, member_id, username, discriminator, nickname
            )

            return MemberResult(200, member=Member(*member.values()))
        except HTTPException as http_e:
            return MemberResult(500, error=f'Unable to get member {member_id}: {http_e.detail}')

    @strawberry.field
    def members(self, guild_id: Snowflake) -> MembersResult:
        try:
            members = resolve.members(guild_id)

            return MembersResult(200, members=members)
        except HTTPException as http_e:
            return MembersResult(404, error=f'Something went wrong while fetching members for guild {guild_id}: '
                                            f'{http_e.detail}')


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
    member_id: Snowflake
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
            guild: Tuple[int, Guild] = resolve.create_guild(_input.guild_id, _input.name)

            return GuildResult(code=guild[0], guild=guild[1])
        except HTTPException as http_e:
            return GuildResult(code=http_e.status_code, error=http_e.detail)

    @strawberry.mutation
    def create_guilds(self, bulk_data: List[Guild.__dict__]) -> GuildsResult:
        try:
            guilds: Tuple[int, Sequence[Guild]] = resolve.create_guilds(bulk_data)

            return GuildsResult(code=guilds[0], guilds=guilds[1])
        except HTTPException as http_e:
            return GuildsResult(code=http_e.status_code, error=http_e.detail)

    @strawberry.mutation
    def update_guild(
            self, guild_id: int, _input: GuildUpdate
    ) -> GuildResult:
        try:
            updated: Tuple[int, Guild] = resolve.update_guild(guild_id, *_input.__dict__.values())

            return GuildResult(updated[0], guild=updated[1])
        except HTTPException as http_e:
            return GuildResult(http_e.status_code, error=f'Cannot update guild {guild_id}: {http_e.detail}')

    @strawberry.mutation
    def delete_guild(self, guild_id: Snowflake) -> DeleteResult:
        try:
            resolve.delete_guild(guild_id)

            return DeleteResult(200, f"{guild_id} successfully deleted.")
        except HTTPException as http_e:
            return DeleteResult(
                http_e.status_code, error=http_e.detail
            )


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
                200,
                member=NewMember(
                    Snowflake(_input.member_id),
                    _input.discriminator,
                    _input.username,
                    _input.nickname,
                ),
            )
        except HTTPException as http_e:
            return MemberResult(500, error=f"{_input.member_id} cannot be created: {http_e.detail}")

    @strawberry.mutation
    def update_member(self, member_id: Snowflake, guild_id: Snowflake, _input: MemberUpdate) -> MemberResult:
        """
        Updates a member_shard row.

        :param member_id: Discord user ID.

        :param guild_id: Discord server ID.

        :param _input: object containing data to update.

        :return: An instance of MemberResult.
        """

        try:
            resolve.update_member_shard(member_id, guild_id, **_input)
            return MemberResult(
                200,
                member=Member(
                    member_id=Snowflake(strawberry.ID(str(member_id))),
                    *_input.__dict__.values()
                ),
            )
        except HTTPException as http_e:
            return MemberResult(500, error=f'')

    @strawberry.mutation
    def delete_member(self, guild_id: Snowflake, member_id: Snowflake) -> DeleteResult:
        try:
            resolve.delete_member_shard(guild_id, member_id)

            return DeleteResult(200, f"{member_id} has been removed from {guild_id}")
        except HTTPException as http_e:
            return DeleteResult(500, f"{member_id} could not be removed from {guild_id}: {http_e.detail}")


@strawberry.type
class Mutation:
    @strawberry.field
    def guild(self) -> GuildMutations:
        return GuildMutations()

    @strawberry.field
    def member(self) -> MemberMutations:
        return MemberMutations()


schema = strawberry.Schema(query=Query, mutation=Mutation)
