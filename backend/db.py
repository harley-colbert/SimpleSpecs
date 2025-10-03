"""Database utilities for SimpleSpecs."""
from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings


@lru_cache(maxsize=1)
def _get_engine():
    """Return the configured SQLModel engine."""

    settings = get_settings()
    return create_engine(settings.DB_URL, echo=False)


def init_db() -> None:
    """Initialise database tables if they do not exist."""

    # Import models for metadata registration.
    from . import db_models  # noqa: F401  # pylint: disable=unused-import

    SQLModel.metadata.create_all(_get_engine())


@contextmanager
def get_session() -> Iterator[Session]:
    """Context manager yielding a SQLModel session."""

    engine = _get_engine()
    with Session(engine) as session:
        yield session
