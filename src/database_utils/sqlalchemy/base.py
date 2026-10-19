from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

DATABASE_NAMING_CONVENTION = {
    "ix": "idx_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class SQLAlchemyBase(DeclarativeBase):
    """Base class for SQLAlchemy declarative models with a consistent naming convention for database constraints."""

    __abstract__ = True
    metadata = MetaData(naming_convention=DATABASE_NAMING_CONVENTION)
