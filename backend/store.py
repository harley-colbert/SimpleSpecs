"""Database scaffolding for SimpleSpecs."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Field, Session, SQLModel, create_engine

from .config import Settings, get_settings

__all__ = [
    "DBParsedObject",
    "DBSectionNode",
    "DBSpecItem",
    "get_session",
]

_ENGINE = None


class DBParsedObject(SQLModel, table=True):
    """Minimal SQLModel stub representing a parsed object."""

    id: int | None = Field(default=None, primary_key=True)


class DBSectionNode(SQLModel, table=True):
    """Minimal SQLModel stub representing a section node."""

    id: int | None = Field(default=None, primary_key=True)


class DBSpecItem(SQLModel, table=True):
    """Minimal SQLModel stub representing a specification item."""

    id: int | None = Field(default=None, primary_key=True)


def get_engine(settings: Settings | None = None):
    """Return a shared SQLModel engine instance."""

    global _ENGINE
    if _ENGINE is None:
        settings = settings or get_settings()
        _ENGINE = create_engine(settings.DB_URL, echo=False)
        SQLModel.metadata.create_all(_ENGINE)
    return _ENGINE


def get_session(settings: Settings | None = None) -> Session:
    """Return a SQLModel session bound to the configured engine."""

    engine = get_engine(settings)
    return Session(engine)


@contextmanager
def session_scope(settings: Settings | None = None) -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""

    session = get_session(settings)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
