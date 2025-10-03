"""FastAPI application entry-point for SimpleSpecs."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import export, health, headers, specs, upload

app = FastAPI(title="SimpleSpecs", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    """Initialise database tables when the application starts."""

    from .db import init_db

    init_db()

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(headers.router)
app.include_router(specs.router)
app.include_router(export.router)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


def create_app() -> FastAPI:
    """Compatibility factory returning the configured application."""

    return app
