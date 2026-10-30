"""Tests for database_utils.sqlalchemy.base module."""
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column

from database_utils.sqlalchemy.base import DATABASE_NAMING_CONVENTION, SQLAlchemyBase


class TestSQLAlchemyBase:
    """Test SQLAlchemyBase declarative base class."""

    def test_sqlalchemy_base_is_abstract(self) -> None:
        """Test that SQLAlchemyBase is marked as abstract."""
        assert SQLAlchemyBase.__abstract__ is True

    def test_sqlalchemy_base_has_naming_convention(self) -> None:
        """Test that SQLAlchemyBase metadata includes naming convention."""
        assert SQLAlchemyBase.metadata.naming_convention is not None
        assert (
            SQLAlchemyBase.metadata.naming_convention
            == DATABASE_NAMING_CONVENTION
        )

    def test_database_naming_convention_has_all_keys(self) -> None:
        """Test that naming convention covers all constraint types."""
        convention = DATABASE_NAMING_CONVENTION
        assert "ix" in convention  # Index
        assert "uq" in convention  # Unique constraint
        assert "ck" in convention  # Check constraint
        assert "fk" in convention  # Foreign key
        assert "pk" in convention  # Primary key

    def test_naming_convention_values(self) -> None:
        """Test naming convention follows expected patterns."""
        convention = DATABASE_NAMING_CONVENTION

        # Index pattern
        assert "%(table_name)s" in convention["ix"]
        assert "idx_" in convention["ix"]

        # Unique constraint pattern
        assert "%(table_name)s" in convention["uq"]
        assert "uq_" in convention["uq"]

        # Check constraint pattern
        assert "%(table_name)s" in convention["ck"]
        assert "ck_" in convention["ck"]

        # Foreign key pattern
        assert "%(table_name)s" in convention["fk"]
        assert "%(referred_table_name)s" in convention["fk"]
        assert "fk_" in convention["fk"]

        # Primary key pattern
        assert "%(table_name)s" in convention["pk"]
        assert "pk_" in convention["pk"]

    def test_sqlalchemy_base_metadata_is_metadata_instance(self) -> None:
        """Test that metadata is a proper MetaData instance."""
        assert isinstance(SQLAlchemyBase.metadata, MetaData)

    def test_subclass_inherits_metadata(self) -> None:
        """Test that subclasses inherit the base metadata configuration."""

        class TestModel(SQLAlchemyBase):
            __tablename__ = "test_models"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column()

        assert TestModel.metadata is SQLAlchemyBase.metadata
        assert (
            TestModel.metadata.naming_convention
            == DATABASE_NAMING_CONVENTION
        )
