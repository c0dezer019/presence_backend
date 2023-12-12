"""
Test to make sure database is properly setup.
"""

import pytest

from app.database import database


class TestDB:
    @pytest.fixture
    def db(self):
        session = database

        yield session

        session.session.close()

    def test_table_creation(self, db):
        assert db.engine.dialect.has_table(db.engine.connect(), "member_shards")
        assert db.engine.dialect.has_table(db.engine.connect(), "guilds")
