"""Shared test fixtures and configuration for database-utils tests."""

from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Mapped, Session, mapped_column

from database_utils.sqlalchemy import (
    SoftDeleteMixin,
    SQLAlchemyBase,
    TimestampMixin,
    create_session_factory,
)


@pytest.fixture
def sqlite_engine() -> Generator[Engine, None, None]:
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLAlchemyBase.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(sqlite_engine: Engine) -> Any:
    """Create a session factory bound to the test engine."""
    return create_session_factory(sqlite_engine)


@pytest.fixture
def session(session_factory: Any) -> Generator[Session, None, None]:
    """Provide a test session."""
    with session_factory() as sess:
        yield sess


# Test models


class User(SQLAlchemyBase, TimestampMixin):
    """Test model with timestamps."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()


class Article(SQLAlchemyBase, TimestampMixin, SoftDeleteMixin):
    """Test model with timestamps and soft delete."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()


class CompositeKeyModel(SQLAlchemyBase):
    """Test model with composite primary key."""

    __tablename__ = "composite_key_models"

    org_id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()


@dataclass
class UserCreate:
    """Create schema for User."""

    name: str
    email: str


@dataclass
class UserUpdate:
    """Update schema for User."""

    name: str | None = None
    email: str | None = None


@dataclass
class ArticleCreate:
    """Create schema for Article."""

    title: str
    content: str


@dataclass
class ArticleUpdate:
    """Update schema for Article."""

    title: str | None = None
    content: str | None = None


@dataclass
class CompositeKeyCreate:
    """Create schema for CompositeKeyModel."""

    org_id: int
    entity_id: int
    name: str


@dataclass
class CompositeKeyUpdate:
    """Update schema for CompositeKeyModel."""

    name: str | None = None
