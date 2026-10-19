from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")
IdType = TypeVar("IdType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class Repository(ABC, Generic[ModelType, IdType, CreateSchemaType, UpdateSchemaType]):
    """Abstract base class for a repository handling instances of ModelType"""

    @abstractmethod
    def list(self) -> Sequence[ModelType]:
        """Return a sequence of all instances"""
        ...

    @abstractmethod
    def get(self, id: IdType) -> ModelType | None:
        """Return a single instance by its ID"""
        ...

    @abstractmethod
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new instance with the provided data"""
        ...

    @abstractmethod
    def update(self, entity: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing instance with the provided data"""
        ...

    @abstractmethod
    def delete(self, entity: ModelType) -> None:
        """Delete an existing instance from the database"""
        ...
