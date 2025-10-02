"""Database engine and session scaffolding."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from backend.config import Settings, get_settings

try:  # pragma: no cover - optional dependency during scaffolding
    from sqlmodel import Session, SQLModel, create_engine
    from sqlalchemy.engine import Engine
except ImportError:  # pragma: no cover
    Session = None  # type: ignore
    SQLModel = None  # type: ignore
    Engine = None  # type: ignore


_engine: Engine | None = None


def init_engine(settings: Settings | None = None) -> Engine:
    """Initialise and cache the SQLModel engine."""

    global _engine
    if _engine is not None:
        return _engine

    settings = settings or get_settings()
    if create_engine is None:  # type: ignore[truthy-function]
        raise RuntimeError("sqlmodel is not installed; cannot create engine")

    _engine = create_engine(settings.DB_URL, echo=False)
    return _engine


@contextmanager
def get_session(settings: Settings | None = None) -> Iterator[Session]:
    """Yield a SQLModel session using the configured engine."""

    if Session is None or SQLModel is None:  # pragma: no cover - handled during runtime
        raise RuntimeError("sqlmodel is not installed; session unavailable")

    engine = init_engine(settings)
    with Session(engine) as session:  # type: ignore[call-arg]
        yield session
