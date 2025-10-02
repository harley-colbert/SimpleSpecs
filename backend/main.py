"""FastAPI application factory for SimpleSpecs."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .logging import setup_logging
from .routers.files import files_router
from .routers.headers import headers_router
from .routers.ingest import ingest_router
from .routers.specs import specs_router
from .routers.system import system_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    setup_logging()
    settings = get_settings()

    app = FastAPI(title="SimpleSpecs", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(ingest_router)
    app.include_router(files_router)
    app.include_router(headers_router)
    app.include_router(specs_router)
    app.include_router(system_router)

    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

    return app
