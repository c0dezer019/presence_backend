import strawberry
from datetime import datetime
from typing import Optional, NewType

from app.database import LocalSession
from app.graphql.resolvers.guild import create_guild

Snowflake = strawberry.scalar(
    NewType("Snowflake", strawberry.ID), serialize=lambda v: v, parse_value=lambda v: v
)


Dict = strawberry.scalar(
    NewType("Dict", dict), serialize=lambda v: v, parse_value=lambda v: v
)


Set = strawberry.scalar(
    NewType("Set", set), serialize=lambda v: v, parse_value=lambda v: v
)

db = LocalSession().session()


@strawberry.interface
class User:
    member_id: Snowflake
    username: str
    discriminator: int
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
    avg_idle_time: Optional[int] = strawberry.UNSET
    recent_avgs: Optional[list[int]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET
    flags: Optional[list[str]] = strawberry.UNSET


@strawberry.type
class MemberResult:
    code: int
    errors: Optional[list[str]] = strawberry.UNSET
    member: Optional[Member | NewMember] = strawberry.UNSET


@strawberry.type
class MembersResult:
    code: int
    errors: Optional[list[str]] = strawberry.UNSET
    members: Optional[Set] = strawberry.UNSET


@strawberry.interface
class Server:
    guild_id: Snowflake
    name: str
    status: Optional[str] = strawberry.UNSET
    settings: Optional[Dict] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET


@strawberry.type
class NewGuild(Server):
    guild_id: Snowflake
    name: str
    date_added: Optional[datetime] = strawberry.UNSET


@strawberry.type
class Guild(Server):
    guild_id: Snowflake
    name: Optional[str] = strawberry.UNSET
    last_activity: Optional[str] = strawberry.UNSET
    last_active_channel: Optional[Snowflake] = strawberry.UNSET
    last_active_ts: Optional[datetime] = strawberry.UNSET
    idle_times: Optional[list[int]] = strawberry.UNSET
    avg_idle_time: Optional[int] = strawberry.UNSET
    recent_avgs: Optional[list[int]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET
    settings: Optional[Dict] = strawberry.UNSET
    members: Optional[Set] = strawberry.UNSET
    date_added: Optional[datetime] = strawberry.UNSET


@strawberry.type
class GuildResult:
    code: int
    errors: Optional[list[str]] = strawberry.UNSET
    guild: Optional[Guild] = strawberry.UNSET


@strawberry.type
class GuildsResult:
    code: int
    errors: Optional[list[str]] = strawberry.UNSET
    guilds: Optional[Set] = strawberry.UNSET


@strawberry.type
class Query:
    members: Optional[MembersResult] = strawberry.UNSET
    member: Optional[MemberResult] = strawberry.UNSET
    guilds: Optional[GuildsResult] = strawberry.UNSET
    guild: Optional[GuildResult] = strawberry.UNSET


@strawberry.type
class DeleteResult:
    code: int
    success_msg: Optional[str] = strawberry.UNSET
    errors: Optional[list[str]] = strawberry.UNSET


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
    avg_idle_time: Optional[int] = strawberry.UNSET
    recent_avgs: Optional[list[int]] = strawberry.UNSET
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
    avg_idle_time: Optional[int] = strawberry.UNSET
    recent_avgs: Optional[list[int]] = strawberry.UNSET
    flags: Optional[list[str]] = strawberry.UNSET
    status: Optional[str] = strawberry.UNSET


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_member(self, input: MemberCreate) -> MemberResult:
        try:
            create_guild(
                member_id=input.member_id,
                username=input.username,
                discriminator=input.discriminator,
            )

            return MemberResult(
                code=200,
                member=NewMember(
                    member_id=Snowflake(input.member_id),
                    discriminator=input.discriminator,
                    username=input.username,
                    nickname=input.nickname,
                    flags=input.flags,
                ),
            )
        except Exception:
            return MemberResult(
                code=500,
                errors=[
                    "An error occurred while trying to create the member. Please try again later."
                ],
            )

    @strawberry.mutation
    def update_member(self, input: MemberUpdate) -> MemberResult:
        return MemberResult(
            code=200,
            member=Member(
                member_id=Snowflake(strawberry.ID(str(input.member_id))),
                username=input.username,
                discriminator=input.discriminator,
            ),
        )

    create_guild: GuildResult
    update_guild: GuildResult
    delete_guild: DeleteResult
    delete_member: DeleteResult


schema = strawberry.Schema(query=Query, mutation=Mutation)
