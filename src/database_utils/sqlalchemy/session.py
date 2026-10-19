from collections.abc import Callable, Generator
from typing import Any, TypeVar

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

_S = TypeVar("_S", bound=Session)


def create_session_factory(
    engine: Engine,
    *,
    class_: type[_S] = Session,  # type: ignore
    autoflush: bool = False,
    expire_on_commit: bool = False,
    info: dict[Any, Any] | None = None,
    **kw: Any,
) -> Callable[..., _S]:
    """Create a SQLAlchemy session factory with the given engine and options.

    Args:
        engine: The SQLAlchemy engine to bind the session to.
        class_: The session class to use, by default Session.
        autoflush: Whether to autoflush the session, by default False.
        expire_on_commit: Whether to expire objects on commit, by default False.
        info: Additional information to associate with the session, by default None.
        **kw: Additional keyword arguments to pass to the sessionmaker.

    Returns:
        A configured SQLAlchemy session factory.
    """
    return sessionmaker(
        bind=engine,
        class_=class_,
        autoflush=autoflush,
        expire_on_commit=expire_on_commit,
        info=info,
        **kw,
    )


def db_session_resource(
    session_factory: Callable[..., _S], autocommit: bool = False
) -> Generator[_S]:
    """Provide a context-managed SQLAlchemy session from the given session factory.

    Args:
        session_factory: The session factory to create sessions from.
        autocommit: Whether to automatically commit the session. Defaults to False.

    Yields:
        A context-managed SQLAlchemy session.
    """
    with session_factory() as session:
        try:
            yield session

            if autocommit:
                session.commit()

        except Exception:
            session.rollback()
            raise
