from collections.abc import Sequence
from dataclasses import asdict
from typing import Any, TypeVar, cast

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from database_utils._internal.utils import is_pydantic_model
from database_utils.abc import CrudRepository, Repository

from .base import SQLAlchemyBase

ModelType = TypeVar("ModelType", bound=SQLAlchemyBase)
IdType = TypeVar("IdType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class SQLAlchemyRepository(Repository[ModelType, IdType]):
    """Simplified SQLAlchemy repository where save operates on model instances.

    Use this when you don't need separate DTOs for creation and updates.
    """

    model_type: type[ModelType]

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a SQLAlchemy session."""
        self.session = session

    def list(self) -> Sequence[ModelType]:
        """Return a sequence of all instances."""
        stmt = select(self.model_type)

        return self.session.scalars(stmt).all()

    def get(self, id: IdType) -> ModelType | None:
        """Return a single instance by its ID."""
        pk = inspect(self.model_type).primary_key

        if isinstance(id, Sequence) and not isinstance(id, (str, bytes)):
            if len(id) != len(pk):
                raise ValueError("Primary key tuple length mismatch")
            pk_comparison = [col == id[i] for i, col in enumerate(pk)]
        else:
            pk_comparison = [pk[0] == id]

        stmt = select(self.model_type).where(*pk_comparison)

        return self.session.scalar(stmt)

    def save(self, entity: ModelType) -> ModelType:
        """Save a model instance (create if new, update if already tracked).

        Detects if the model is already tracked in the session:
        - If tracked: performs flush and refresh
        - If not tracked: adds to session, then flush and refresh
        """
        # Check if model is already in the session
        if entity not in self.session:
            self.session.add(entity)

        self.session.flush()
        self.session.refresh(entity)

        return entity

    def delete(self, entity: ModelType) -> None:
        """Delete an existing instance from the database."""
        self.session.delete(entity)


class SQLAlchemyCrudRepository(
    SQLAlchemyRepository[ModelType, IdType],
    CrudRepository[ModelType, IdType],
):
    """SQLAlchemy implementation of CrudRepository with separate create/update schemas."""

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new instance with the provided data."""
        if is_pydantic_model(obj_in):
            data = obj_in.model_dump()
        else:
            data = asdict(cast(Any, obj_in))

        entity = self.model_type(**data)

        return self.save(entity)

    def update(self, entity: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Update an existing instance with the provided data."""
        if is_pydantic_model(obj_in):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = asdict(cast(Any, obj_in))
            update_data = {k: v for k, v in update_data.items() if v is not None}

        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)

        return self.save(entity)
