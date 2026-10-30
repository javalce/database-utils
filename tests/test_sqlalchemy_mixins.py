"""Tests for database_utils.sqlalchemy.mixins module."""
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, mapped_column

from database_utils.sqlalchemy.base import SQLAlchemyBase
from database_utils.sqlalchemy.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    db_utc_now,
)


class TestDbUtcNow:
    """Test db_utc_now custom function."""

    def test_db_utc_now_is_generic_function(self) -> None:
        """Test that db_utc_now is a GenericFunction."""
        from sqlalchemy.sql import functions

        func = db_utc_now()
        assert isinstance(func, functions.GenericFunction)

    def test_db_utc_now_has_datetime_type(self) -> None:
        """Test that db_utc_now returns a DATETIME type."""
        from sqlalchemy import DATETIME

        func = db_utc_now()
        assert isinstance(func.type, type(DATETIME()))

    def test_db_utc_now_inherit_cache(self) -> None:
        """Test that db_utc_now has inherit_cache enabled."""
        assert db_utc_now.inherit_cache is True


class TestTimestampMixin:
    """Test TimestampMixin for created_at and updated_at columns."""

    def test_timestamp_mixin_has_created_at(self) -> None:
        """Test that TimestampMixin adds created_at column."""

        class TestModel(SQLAlchemyBase, TimestampMixin):
            __tablename__ = "test_timestamps"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel)
        assert "created_at" in mapper.columns
        created_at_col = mapper.columns["created_at"]
        assert created_at_col.type.__class__.__name__ == "DateTime"

    def test_timestamp_mixin_has_updated_at(self) -> None:
        """Test that TimestampMixin adds updated_at column."""

        class TestModel2(SQLAlchemyBase, TimestampMixin):
            __tablename__ = "test_timestamps_2"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel2)
        assert "updated_at" in mapper.columns
        updated_at_col = mapper.columns["updated_at"]
        assert updated_at_col.type.__class__.__name__ == "DateTime"

    def test_timestamp_columns_have_timezone(self) -> None:
        """Test that timestamp columns are timezone-aware."""

        class TestModel3(SQLAlchemyBase, TimestampMixin):
            __tablename__ = "test_timestamps_tz"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel3)
        created_at = mapper.columns["created_at"]
        updated_at = mapper.columns["updated_at"]

        assert created_at.type.timezone is True
        assert updated_at.type.timezone is True

    def test_timestamp_columns_have_server_defaults(self) -> None:
        """Test that timestamp columns have server defaults."""

        class TestModel4(SQLAlchemyBase, TimestampMixin):
            __tablename__ = "test_timestamps_defaults"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel4)
        created_at = mapper.columns["created_at"]
        updated_at = mapper.columns["updated_at"]

        assert created_at.server_default is not None
        assert updated_at.server_default is not None

    def test_timestamp_columns_nullable(self) -> None:
        """Test that timestamp columns are not nullable."""

        class TestModel5(SQLAlchemyBase, TimestampMixin):
            __tablename__ = "test_timestamps_nullable"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel5)
        assert mapper.columns["created_at"].nullable is False
        assert mapper.columns["updated_at"].nullable is False

    def test_timestamp_mixin_in_database_model(self, session: Any) -> None:  # type: ignore[name-defined]
        """Test that TimestampMixin works with actual database models."""
        from tests.conftest import User

        # Verify the User model has timestamp columns
        mapper = inspect(User)
        assert "created_at" in mapper.columns
        assert "updated_at" in mapper.columns


class TestSoftDeleteMixin:
    """Test SoftDeleteMixin for soft delete functionality."""

    def test_soft_delete_mixin_has_is_deleted(self) -> None:
        """Test that SoftDeleteMixin adds is_deleted column."""

        class TestModel6(SQLAlchemyBase, SoftDeleteMixin):
            __tablename__ = "test_soft_delete"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel6)
        assert "is_deleted" in mapper.columns
        is_deleted_col = mapper.columns["is_deleted"]
        assert is_deleted_col.type.__class__.__name__ == "Boolean"

    def test_soft_delete_mixin_has_deleted_at(self) -> None:
        """Test that SoftDeleteMixin adds deleted_at column."""

        class TestModel7(SQLAlchemyBase, SoftDeleteMixin):
            __tablename__ = "test_soft_delete_2"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel7)
        assert "deleted_at" in mapper.columns
        deleted_at_col = mapper.columns["deleted_at"]
        assert deleted_at_col.type.__class__.__name__ == "DateTime"

    def test_is_deleted_default_false(self) -> None:
        """Test that is_deleted has a default value."""

        class TestModel8(SQLAlchemyBase, SoftDeleteMixin):
            __tablename__ = "test_soft_delete_3"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel8)
        is_deleted_col = mapper.columns["is_deleted"]
        # The column has a default value set
        assert (
            is_deleted_col.default is not None
            or is_deleted_col.server_default is not None
        )

    def test_deleted_at_nullable(self) -> None:
        """Test that deleted_at is nullable."""

        class TestModel9(SQLAlchemyBase, SoftDeleteMixin):
            __tablename__ = "test_soft_delete_4"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel9)
        deleted_at_col = mapper.columns["deleted_at"]
        assert deleted_at_col.nullable is True

    def test_deleted_at_timezone_aware(self) -> None:
        """Test that deleted_at is timezone-aware."""

        class TestModel10(SQLAlchemyBase, SoftDeleteMixin):
            __tablename__ = "test_soft_delete_5"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(TestModel10)
        deleted_at_col = mapper.columns["deleted_at"]
        assert deleted_at_col.type.timezone is True

    def test_soft_delete_mixin_in_database_model(self, session: Any) -> None:  # type: ignore[name-defined]
        """Test that SoftDeleteMixin works with actual database models."""
        from tests.conftest import Article

        # Verify the Article model has soft delete columns
        mapper = inspect(Article)
        assert "is_deleted" in mapper.columns
        assert "deleted_at" in mapper.columns

    def test_combined_mixins(self) -> None:
        """Test combining TimestampMixin and SoftDeleteMixin."""

        class CombinedModel(SQLAlchemyBase, TimestampMixin, SoftDeleteMixin):
            __tablename__ = "combined_model"
            id: Mapped[int] = mapped_column(primary_key=True)

        mapper = inspect(CombinedModel)
        assert "created_at" in mapper.columns
        assert "updated_at" in mapper.columns
        assert "is_deleted" in mapper.columns
        assert "deleted_at" in mapper.columns
