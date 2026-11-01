from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")
IdType = TypeVar("IdType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class Repository(ABC, Generic[ModelType, IdType]):
    """Abstract base class for a simplified repository where the model is the schema.

    This interface is for simpler use cases where save and delete operate directly
    on model instances without separate DTOs or schemas.
    """

    @abstractmethod
    def list(self) -> Sequence[ModelType]:
        """Return a sequence of all instances"""
        ...

    @abstractmethod
    def get(self, id: IdType) -> ModelType | None:
        """Return a single instance by its ID"""
        ...

    @abstractmethod
    def save(self, entity: ModelType) -> ModelType:
        """Save a model instance (create if new, update if already tracked)"""
        ...

    @abstractmethod
    def delete(self, entity: ModelType) -> None:
        """Delete a model instance from the database"""
        ...


class CrudRepository(Repository[ModelType, IdType]):
    """Abstract base class for a repository handling instances of ModelType with separate schemas.

    Extends Repository to support separate DTOs for creation and update operations.
    """

    @abstractmethod
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new instance with the provided data"""
        ...

    @abstractmethod
    def update(self, entity: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing instance with the provided data"""
        ...
