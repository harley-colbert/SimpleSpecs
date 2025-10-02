"""Database scaffolding for SimpleSpecs."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import Settings, get_settings

_ENGINE = None


def get_engine(settings: Settings | None = None):
    """Return a shared SQLModel engine instance."""

    global _ENGINE
    if _ENGINE is None:
        settings = settings or get_settings()
        _ENGINE = create_engine(settings.DB_URL, echo=False)
        SQLModel.metadata.create_all(_ENGINE)
    return _ENGINE


@contextmanager
def session_scope(settings: Settings | None = None) -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""

    engine = get_engine(settings)
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
