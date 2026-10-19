import datetime as dt
from typing import Any

from sqlalchemy import DATETIME, Boolean, ClauseElement, DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import functions
from sqlalchemy.sql.compiler import SQLCompiler


class db_utc_now(functions.GenericFunction):  # type: ignore
    """Database-side UTC timestamp. Guarantees UTC regardless of server timezone."""

    type = DATETIME()
    inherit_cache = True


@compiles(db_utc_now, "postgresql")
def _pg_utc_now(element: ClauseElement, compiler: SQLCompiler, **kw: Any) -> str:
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@compiles(db_utc_now, "sqlite")
def _sqlite_utc_now(element: ClauseElement, compiler: SQLCompiler, **kw: Any) -> str:
    return "datetime('now')"


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamp columns."""

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=db_utc_now()
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=db_utc_now(), onupdate=db_utc_now()
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete functionality with is_deleted and deleted_at columns."""

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[dt.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
