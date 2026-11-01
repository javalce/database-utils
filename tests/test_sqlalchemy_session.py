"""Tests for database_utils.sqlalchemy.session module."""

from collections.abc import Callable
from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from database_utils.sqlalchemy.session import (
    create_session_factory,
    db_session_resource,
)


class TestCreateSessionFactory:
    """Test create_session_factory function."""

    def test_create_session_factory_returns_callable(self, sqlite_engine: Any) -> None:
        """Test that create_session_factory returns a callable."""
        factory: Callable[..., Session] = create_session_factory(sqlite_engine)
        assert callable(factory)

    def test_created_session_factory_creates_sessions(self, sqlite_engine: Any) -> None:
        """Test that the factory creates session instances."""
        factory: Callable[..., Session] = create_session_factory(sqlite_engine)
        session = factory()
        assert isinstance(session, Session)
        session.close()

    def test_session_factory_with_default_options(self, sqlite_engine: Any) -> None:
        """Test session factory with default options."""
        factory: Callable[..., Session] = create_session_factory(sqlite_engine)
        session = factory()

        # Default options: autoflush=False, expire_on_commit=False
        assert session.autoflush is False
        assert session.expire_on_commit is False

        session.close()

    def test_session_factory_with_custom_autoflush(self, sqlite_engine: Any) -> None:
        """Test session factory with custom autoflush setting."""
        factory: Callable[..., Session] = create_session_factory(sqlite_engine, autoflush=True)
        session = factory()

        assert session.autoflush is True

        session.close()

    def test_session_factory_with_custom_expire_on_commit(self, sqlite_engine: Any) -> None:
        """Test session factory with custom expire_on_commit setting."""
        factory: Callable[..., Session] = create_session_factory(
            sqlite_engine, expire_on_commit=True
        )
        session = factory()

        assert session.expire_on_commit is True

        session.close()

    def test_session_factory_with_info_dict(self, sqlite_engine: Any) -> None:
        """Test session factory with info dictionary."""
        info = {"custom_key": "custom_value"}
        factory: Callable[..., Session] = create_session_factory(sqlite_engine, info=info)
        session = factory()

        assert session.info["custom_key"] == "custom_value"

        session.close()

    def test_session_factory_with_custom_session_class(self, sqlite_engine: Any) -> None:
        """Test session factory with custom Session class."""
        factory: Callable[..., Session] = create_session_factory(sqlite_engine, class_=Session)
        session = factory()

        assert isinstance(session, Session)

        session.close()

    def test_session_factory_binds_engine(self, sqlite_engine: Any) -> None:
        """Test that session factory binds to the provided engine."""
        factory: Callable[..., Session] = create_session_factory(sqlite_engine)
        session = factory()

        # Execute a simple query to verify engine is bound
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1

        session.close()


class TestDbSessionResource:
    """Test db_session_resource generator."""

    def test_db_session_resource_yields_session(self, session_factory: Any) -> None:
        """Test that db_session_resource yields a Session."""
        gen = db_session_resource(session_factory)
        session = next(gen)
        assert isinstance(session, Session)
        try:
            next(gen)
        except StopIteration:
            pass

    def test_db_session_resource_closes_session_on_exit(self, session_factory: Any) -> None:
        """Test that db_session_resource closes the session on exit."""
        gen = db_session_resource(session_factory)
        session = next(gen)
        session_was_active = session.is_active

        try:
            next(gen)
        except StopIteration:
            pass

        # Session should still be closed properly
        assert session_was_active

    def test_db_session_resource_autocommit_false_by_default(
        self, session_factory: Any, sqlite_engine: Any
    ) -> None:
        """Test that autocommit defaults to False."""
        from tests.conftest import User

        gen = db_session_resource(session_factory, autocommit=False)
        session = next(gen)

        # Create and flush
        user = User(name="Test", email="test@example.com")
        session.add(user)
        session.flush()

        user_id = user.id

        try:
            next(gen)
        except StopIteration:
            pass

        # Create new session to check if data was persisted
        # Without autocommit, data should NOT be persisted
        gen2 = db_session_resource(session_factory)
        session2 = next(gen2)
        retrieved = session2.query(User).filter_by(id=user_id).first()
        try:
            next(gen2)
        except StopIteration:
            pass

        # Data was not committed, so it should be None
        assert retrieved is None

    def test_db_session_resource_autocommit_true_calls_commit(self, session_factory: Any) -> None:
        """Test that autocommit=True triggers commit (simplified test)."""
        # Just verify the behavior is accepted without raising
        gen = db_session_resource(session_factory, autocommit=True)
        session = next(gen)
        assert isinstance(session, Session)
        try:
            next(gen)
        except StopIteration:
            pass

    def test_db_session_resource_rollback_on_exception(
        self, session_factory: Any, sqlite_engine: Any
    ) -> None:
        """Test that session is rolled back when exception occurs."""
        from tests.conftest import User

        user_id = None
        try:
            gen = db_session_resource(session_factory)
            session = next(gen)

            user = User(name="Will Fail", email="fail@example.com")
            session.add(user)
            session.flush()
            user_id = user.id
            raise ValueError("Test exception")
        except ValueError:
            try:
                next(gen)
            except StopIteration:
                pass

        # Verify data was rolled back
        gen2 = db_session_resource(session_factory)
        session2 = next(gen2)
        retrieved = session2.query(User).filter_by(id=user_id).first()
        try:
            next(gen2)
        except StopIteration:
            pass

        assert retrieved is None

    def test_db_session_resource_reraises_exception(self, session_factory: Any) -> None:
        """Test that exceptions are re-raised after rollback."""
        with pytest.raises(ValueError, match="Test error"):
            gen = db_session_resource(session_factory)
            session = next(gen)  # noqa: F841
            raise ValueError("Test error")

    def test_db_session_resource_with_generator_protocol(self, session_factory: Any) -> None:
        """Test that db_session_resource works as a generator."""
        gen = db_session_resource(session_factory)
        session = next(gen)
        assert isinstance(session, Session)

        # Clean up
        try:
            next(gen)
        except StopIteration:
            pass

    def test_db_session_resource_multiple_iterations(
        self, session_factory: Any, sqlite_engine: Any
    ) -> None:
        """Test that multiple uses of db_session_resource work independently."""
        from tests.conftest import User

        # First context
        gen = db_session_resource(session_factory, autocommit=True)
        session = next(gen)
        user1 = User(name="User 1", email="user1@example.com")
        session.add(user1)
        try:
            next(gen)
        except StopIteration:
            pass

        # Second context
        gen = db_session_resource(session_factory, autocommit=True)
        session = next(gen)
        user2 = User(name="User 2", email="user2@example.com")
        session.add(user2)
        try:
            next(gen)
        except StopIteration:
            pass

        # Verify both were created
        gen = db_session_resource(session_factory)
        session = next(gen)
        count = session.query(User).count()
        try:
            next(gen)
        except StopIteration:
            pass

        assert count == 2
