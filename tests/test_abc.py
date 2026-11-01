"""Tests for database_utils.abc module."""

from collections.abc import Sequence
from typing import Any

import pytest

from database_utils.abc import CrudRepository


class MockModel:
    """Mock model for testing."""

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name


class MockRepository(CrudRepository[MockModel, int]):
    """Concrete implementation of CrudRepository for testing."""

    def __init__(self) -> None:
        self.data: dict[int, MockModel] = {}
        self.counter = 0

    def list(self) -> Sequence[MockModel]:
        """Return all models."""
        return list(self.data.values())

    def get(self, id: int) -> MockModel | None:
        """Return a model by ID."""
        return self.data.get(id)

    def save(self, entity: MockModel) -> MockModel:
        """Save a model instance."""
        if entity.id is not None and entity.id in self.data:
            # Update existing
            self.data[entity.id] = entity
        elif entity.id is None or entity.id not in self.data:
            # Create new
            self.counter += 1
            entity.id = self.counter
            self.data[self.counter] = entity
        return entity

    def create(self, obj_in: dict[str, Any]) -> MockModel:
        """Create a new model."""
        self.counter += 1
        model = MockModel(self.counter, obj_in["name"])
        self.data[self.counter] = model
        return model

    def update(self, entity: MockModel, obj_in: dict[str, Any]) -> MockModel:
        """Update an existing model."""
        if "name" in obj_in:
            entity.name = obj_in["name"]
        return entity

    def delete(self, entity: MockModel) -> None:
        """Delete a model."""
        if entity.id in self.data:
            del self.data[entity.id]


class TestRepository:
    """Test Repository abstract base class."""

    def test_repository_is_abstract(self) -> None:
        """Test that Repository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CrudRepository()  # type: ignore[call-arg]

    def test_repository_requires_list_implementation(self) -> None:
        """Test that concrete implementations must implement list()."""

        class IncompleteRepo(CrudRepository):  # type: ignore[type-arg]
            pass

        with pytest.raises(TypeError):
            IncompleteRepo()  # type: ignore[call-arg]

    def test_mock_repository_implements_all_methods(self) -> None:
        """Test that MockRepository successfully implements all abstract methods."""
        repo = MockRepository()
        assert hasattr(repo, "list")
        assert hasattr(repo, "get")
        assert hasattr(repo, "create")
        assert hasattr(repo, "update")
        assert hasattr(repo, "delete")
        assert hasattr(repo, "save")

    def test_mock_repository_list(self) -> None:
        """Test list() returns all instances."""
        repo = MockRepository()
        repo.create({"name": "Alice"})
        repo.create({"name": "Bob"})

        items = repo.list()
        assert len(items) == 2
        assert items[0].name == "Alice"
        assert items[1].name == "Bob"

    def test_mock_repository_get(self) -> None:
        """Test get() returns a single instance by ID."""
        repo = MockRepository()
        alice = repo.create({"name": "Alice"})

        retrieved = repo.get(alice.id)
        assert retrieved is not None
        assert retrieved.id == alice.id
        assert retrieved.name == "Alice"

    def test_mock_repository_get_missing(self) -> None:
        """Test get() returns None for missing ID."""
        repo = MockRepository()
        result = repo.get(9999)
        assert result is None

    def test_mock_repository_create(self) -> None:
        """Test create() adds a new instance."""
        repo = MockRepository()
        model = repo.create({"name": "Charlie"})

        assert model.id is not None
        assert model.name == "Charlie"
        assert len(repo.list()) == 1

    def test_mock_repository_update(self) -> None:
        """Test update() modifies an existing instance."""
        repo = MockRepository()
        model = repo.create({"name": "David"})
        updated = repo.update(model, {"name": "David Updated"})

        assert updated.name == "David Updated"
        retrieved = repo.get(model.id)
        assert retrieved is not None
        assert retrieved.name == "David Updated"

    def test_mock_repository_delete(self) -> None:
        """Test delete() removes an instance."""
        repo = MockRepository()
        model = repo.create({"name": "Eve"})
        repo.delete(model)

        assert repo.get(model.id) is None
        assert len(repo.list()) == 0

    def test_repository_contract_with_none_values(self) -> None:
        """Test repository handles None returns gracefully."""
        repo = MockRepository()
        assert repo.get(0) is None
        assert isinstance(repo.list(), Sequence)
