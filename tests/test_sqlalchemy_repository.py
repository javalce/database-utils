"""Tests for database_utils.sqlalchemy.repository SQLAlchemyRepository."""

from collections.abc import Sequence
from typing import Any

from database_utils.sqlalchemy import SQLAlchemyRepository


class TestSQLAlchemyRepository:
    """Test SQLAlchemyRepository save/delete operations."""

    def test_repository_requires_model_type(self) -> None:
        """Test that repository requires model_type to be set."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        # Should not raise
        assert UserRepository.model_type is User

    def test_repository_initialization(self, session: Any) -> None:
        """Test repository initialization with a session."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        assert repo.session is session

    def test_save_new_model(self, session: Any) -> None:
        """Test saving a new model instance."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        user = User(name="Alice", email="alice@example.com")

        saved = repo.save(user)

        assert saved.id is not None
        assert saved.name == "Alice"
        assert saved.email == "alice@example.com"

    def test_save_existing_model(self, session: Any) -> None:
        """Test saving an existing model that's already tracked."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        # Create and save
        user = User(name="Bob", email="bob@example.com")
        saved = repo.save(user)
        original_id = saved.id

        # Modify and save again
        saved.name = "Bob Updated"
        updated = repo.save(saved)

        assert updated.id == original_id
        assert updated.name == "Bob Updated"

    def test_list_empty(self, session: Any) -> None:
        """Test listing when no entities exist."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        users = repo.list()

        assert isinstance(users, Sequence)
        assert len(users) == 0

    def test_list_returns_all_entities(self, session: Any) -> None:
        """Test list() returns all saved entities."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        user1 = User(name="Charlie", email="charlie@example.com")
        user2 = User(name="Diana", email="diana@example.com")
        repo.save(user1)
        repo.save(user2)

        users = repo.list()

        assert len(users) == 2
        assert users[0].name in ["Charlie", "Diana"]
        assert users[1].name in ["Charlie", "Diana"]

    def test_get_returns_entity_by_id(self, session: Any) -> None:
        """Test get() returns entity by primary key."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        user = User(name="Eve", email="eve@example.com")
        saved = repo.save(user)

        retrieved = repo.get(saved.id)

        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.name == "Eve"

    def test_get_returns_none_for_missing_id(self, session: Any) -> None:
        """Test get() returns None when entity doesn't exist."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        result = repo.get(9999)

        assert result is None

    def test_delete_entity(self, session: Any) -> None:
        """Test delete() removes an entity from the session."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        user = User(name="Frank", email="frank@example.com")
        saved = repo.save(user)

        repo.delete(saved)

        # The entity is marked for deletion
        assert saved in session.deleted

    def test_composite_primary_key_get(self, session: Any) -> None:
        """Test get() with composite primary key."""
        from tests.conftest import CompositeKeyModel

        class CompositeRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = CompositeKeyModel

        repo = CompositeRepository(session)

        # Create and save entity
        entity = CompositeKeyModel(org_id=1, entity_id=100, name="Test")
        repo.save(entity)

        # Get by composite key tuple
        retrieved = repo.get((1, 100))

        assert retrieved is not None
        assert retrieved.org_id == 1
        assert retrieved.entity_id == 100
        assert retrieved.name == "Test"

    def test_save_after_get(self, session: Any) -> None:
        """Test that get returns a tracked instance that can be saved."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        # Create initial user
        user = User(name="Grace", email="grace@example.com")
        repo.save(user)
        user_id = user.id

        # Get the user (already tracked)
        retrieved = repo.get(user_id)
        assert retrieved is not None

        # Modify and save
        retrieved.name = "Grace Updated"
        saved = repo.save(retrieved)

        assert saved.id == user_id
        assert saved.name == "Grace Updated"
