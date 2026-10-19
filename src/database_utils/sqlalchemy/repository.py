from collections.abc import Sequence
from dataclasses import asdict
from typing import Any, TypeVar, cast

from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from database_utils._internal.utils import is_pydantic_model
from database_utils.abc import Repository

from .base import SQLAlchemyBase

ModelType = TypeVar("ModelType", bound=SQLAlchemyBase)
IdType = TypeVar("IdType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class SQLAlchemyRepository(Repository[ModelType, IdType, CreateSchemaType, UpdateSchemaType]):
    """SQLAlchemy implementation of the Repository abstract base class."""

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

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new instance with the provided data."""
        if is_pydantic_model(obj_in):
            data = obj_in.model_dump()
        else:
            data = asdict(cast(Any, obj_in))

        entity = self.model_type(**data)

        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)

        return entity

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

        self.session.flush()
        self.session.refresh(entity)

        return entity

    def delete(self, entity: ModelType) -> None:
        """Delete an existing instance from the database."""
        self.session.delete(entity)
