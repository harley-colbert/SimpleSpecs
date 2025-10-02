"""FastAPI application factory for SimpleSpecs."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import Settings, get_settings
from backend.logging import setup_logging
from backend.routers.files import files_router
from backend.routers.headers import headers_router
from backend.routers.ingest import ingest_router
from backend.routers.specs import specs_router
from backend.routers.system import system_router


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    setup_logging()
    settings = settings or get_settings()

    app = FastAPI(title="SimpleSpecs", version="0.1.0")
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if FRONTEND_DIR.exists():
        app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    async def serve_index() -> FileResponse:
        """Serve the frontend index file."""

        index_file = FRONTEND_DIR / "index.html"
        return FileResponse(index_file) if index_file.exists() else FileResponse("frontend/index.html")

    @app.get("/healthz", summary="Health check")
    async def healthz() -> dict[str, str]:
        """Simple health check endpoint."""

        return {"status": "ok"}

    app.include_router(ingest_router)
    app.include_router(files_router)
    app.include_router(headers_router)
    app.include_router(specs_router)
    app.include_router(system_router)

    return app


__all__ = ["create_app"]
