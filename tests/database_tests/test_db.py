"""
Test to make sure database is properly setup.
"""

import pytest

from app.database import db


class TestDB:
    @pytest.fixture
    def db(self):
        session = db

        yield session

        session.session.close()

    def test_table_creation(self, db):
        assert db.engine.dialect.has_table(db.engine.connect(), "member_shards")
        assert db.engine.dialect.has_table(db.engine.connect(), "guilds")
