import pytest
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

from app.database import engine
from app.database.models import Base, Guild, MemberShard
from app.graphql.resolvers import Resolver

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


class TestResolvers:
    @pytest.fixture(scope="class")
    def resolver(self):
        return Resolver()

    @pytest.fixture(scope="class")
    def guild(self, resolver):
        guild_id = 1234
        name = "Test Guild"
        instance = resolver.guild(guild_id, name)

        return instance

    @pytest.fixture(scope="class")
    def member(self, resolver):
        guild_id = 1234
        guild_name = "Test Guild"
        member_id = 456
        username = "Test User"
        discriminator = 1234

        member = resolver.member(guild_id, guild_name, member_id, username, discriminator)

        return member

    def test_create_guild_success(self, resolver, guild):
        guild_id = 1234
        name = "Test Guild"

        assert isinstance(guild, Guild)
        assert guild.guild_id == guild_id
        assert guild.name == name
        assert guild in resolver.db

    def test_create_member_success(self, resolver, member, guild):
        member_id = 456
        username = "Test User"
        discriminator = 1234

        assert isinstance(member, MemberShard)
        assert member.member_id == member_id
        assert member.username == username
        assert member.discriminator == discriminator
        assert member.guild_id == guild.guild_id
        assert member in resolver.db

    def test_update_existing_guild_with_valid_guild_id_and_kwargs(self, resolver):
        updated_guild = resolver.update_guild(1234, name="Updated Guild Name")

        assert isinstance(updated_guild, Guild)
        assert updated_guild.guild_id == 1234
        assert updated_guild.name == "Updated Guild Name"

    def test_create_new_guild_with_existing_guild_id_raises_http_exception(self, resolver):

        with pytest.raises(HTTPException) as exc_info:
            resolver.guild(1234, "Test Guild2")

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "You cannot create another guild with a duplicate ID."

    def test_create_a_member_shard_with_a_duplicate_discriminator(self, resolver):
        with pytest.raises(HTTPException) as exc_info:
            resolver.member(1234, "Test Guild", 789, "Test User", 1234)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "You cannot create another member with a duplicate discriminator."

    def test_update_non_existing_guild(self, resolver):
        with pytest.raises(NoResultFound):
            resolver.update_guild(1235, name="Updated Guild Name")

    def test_update_non_existing_member(self, resolver):
        with pytest.raises(NoResultFound):
            resolver.update_member_shard(12345, 1234, nickname="Joe")

    def test_delete_guild(self, guild, resolver):
        deleted_guild = resolver.delete_guild(guild.guild_id)

        assert isinstance(deleted_guild, Guild)

    def test_delete_member(self, guild, member, resolver):
        deleted_member = resolver.delete_member_shard(guild.guild_id, member.member_id)

        assert isinstance(deleted_member, MemberShard)

    def test_prune_members(self, guild, member, resolver):
        pruned_members = resolver.prune(guild.guild_id)

        assert len(pruned_members) > 0
        assert member in pruned_members
