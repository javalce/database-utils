"""Tests for database_utils.sqlalchemy.repository module."""
from collections.abc import Sequence
from typing import Any

import pytest

from database_utils.sqlalchemy import SQLAlchemyRepository


class TestSQLAlchemyRepository:
    """Test SQLAlchemyRepository CRUD operations."""

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

    def test_create_with_dataclass_schema(self, session: Any) -> None:
        """Test creating an entity with dataclass schema."""
        from tests.conftest import User, UserCreate

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        user_in = UserCreate(name="Alice", email="alice@example.com")

        user = repo.create(user_in)

        assert user.id is not None
        assert user.name == "Alice"
        assert user.email == "alice@example.com"

    def test_create_with_pydantic_model(self, session: Any) -> None:
        """Test creating an entity with Pydantic model."""
        from tests.conftest import User

        try:
            from pydantic import BaseModel

            class UserCreatePydantic(BaseModel):
                name: str
                email: str

            class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
                model_type = User

            repo = UserRepository(session)
            user_in = UserCreatePydantic(name="Charlie", email="charlie@example.com")

            user = repo.create(user_in)

            assert user.id is not None
            assert user.name == "Charlie"
        except ImportError:
            pytest.skip("pydantic not installed")

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
        """Test list() returns all created entities."""
        from tests.conftest import User, UserCreate

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        repo.create(UserCreate(name="David", email="david@example.com"))
        repo.create(UserCreate(name="Eve", email="eve@example.com"))

        users = repo.list()

        assert len(users) == 2
        assert users[0].name in ["David", "Eve"]
        assert users[1].name in ["David", "Eve"]

    def test_get_returns_entity_by_id(self, session: Any) -> None:
        """Test get() returns entity by primary key."""
        from tests.conftest import User, UserCreate

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        created = repo.create(UserCreate(name="Frank", email="frank@example.com"))

        retrieved = repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Frank"

    def test_get_returns_none_for_missing_id(self, session: Any) -> None:
        """Test get() returns None when entity doesn't exist."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        result = repo.get(9999)

        assert result is None

    def test_update_with_dataclass(self, session: Any) -> None:
        """Test update() with dataclass schema."""
        from tests.conftest import User, UserCreate, UserUpdate

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        created = repo.create(UserCreate(name="Grace", email="grace@example.com"))

        updated = repo.update(created, UserUpdate(name="Grace Updated"))

        assert updated.name == "Grace Updated"
        assert updated.email == "grace@example.com"

    def test_update_with_pydantic(self, session: Any) -> None:
        """Test update() with Pydantic model."""
        from tests.conftest import User, UserCreate

        try:
            from pydantic import BaseModel

            class UserUpdatePydantic(BaseModel):
                name: str | None = None
                email: str | None = None

            class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
                model_type = User

            repo = UserRepository(session)
            created = repo.create(UserCreate(name="Ivy", email="ivy@example.com"))

            updated = repo.update(created, UserUpdatePydantic(name="Ivy Updated"))

            assert updated.name == "Ivy Updated"
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_update_partial_fields(self, session: Any) -> None:
        """Test that update only modifies specified fields."""
        from tests.conftest import User, UserCreate, UserUpdate

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        created = repo.create(UserCreate(name="Jack", email="jack@example.com"))

        # Update only name
        updated = repo.update(created, UserUpdate(name="Jack Updated", email=None))

        assert updated.name == "Jack Updated"
        assert updated.email == "jack@example.com"

    def test_delete_entity(self, session: Any) -> None:
        """Test delete() removes an entity from the session."""
        from tests.conftest import User, UserCreate

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        created = repo.create(UserCreate(name="Karen", email="karen@example.com"))

        # Delete should work (it just marks for deletion in the session)
        repo.delete(created)

        # The entity is marked for deletion but still in the session
        # After session commit/flush it would be removed from DB
        assert created in session.deleted

    def test_composite_primary_key_get(self, session: Any) -> None:
        """Test get() with composite primary key."""
        from tests.conftest import CompositeKeyModel

        class CompositeRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = CompositeKeyModel

        repo = CompositeRepository(session)

        # Create entity
        entity = CompositeKeyModel(org_id=1, entity_id=100, name="Test")
        session.add(entity)
        session.flush()

        # Get by composite key tuple
        retrieved = repo.get((1, 100))

        assert retrieved is not None
        assert retrieved.org_id == 1
        assert retrieved.entity_id == 100
        assert retrieved.name == "Test"

    def test_composite_primary_key_mismatch_raises_error(self, session: Any) -> None:
        """Test that composite key length mismatch raises ValueError."""
        from tests.conftest import CompositeKeyModel

        class CompositeRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = CompositeKeyModel

        repo = CompositeRepository(session)

        # Try to get with wrong tuple length
        with pytest.raises(ValueError, match="Primary key tuple length mismatch"):
            repo.get((1,))  # Only one value, expects two

    def test_list_returns_sequence_type(self, session: Any) -> None:
        """Test that list() returns a proper Sequence."""
        from tests.conftest import User

        class UserRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = User

        repo = UserRepository(session)
        result = repo.list()

        assert isinstance(result, Sequence)
        assert hasattr(result, "__len__")
        assert hasattr(result, "__getitem__")

    def test_repository_persists_timestamps(self, session: Any) -> None:
        """Test that created/updated timestamps are set."""
        from tests.conftest import Article, ArticleCreate

        class ArticleRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = Article

        repo = ArticleRepository(session)
        article = repo.create(ArticleCreate(title="Test", content="Content"))

        assert article.created_at is not None
        assert article.updated_at is not None

    def test_repository_with_soft_delete_mixin(self, session: Any) -> None:
        """Test repository works with soft delete models."""
        from tests.conftest import Article, ArticleCreate

        class ArticleRepository(SQLAlchemyRepository):  # type: ignore[misc]
            model_type = Article

        repo = ArticleRepository(session)
        article = repo.create(ArticleCreate(title="Delete Test", content="Content"))

        # Verify soft delete fields exist
        assert article.is_deleted is False
        assert article.deleted_at is None
