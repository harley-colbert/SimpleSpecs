"""Ingest routes."""
from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter

from backend.config import get_settings


ingest_router = APIRouter(prefix="/ingest", tags=["ingest"])


@ingest_router.post("", summary="Upload a file and create an ingestion record.")
def ingest_file() -> dict[str, Any]:
    """Mock ingestion endpoint returning a generated file identifier."""

    file_id = f"file-{uuid.uuid4().hex[:8]}"
    settings = get_settings()
    return {
        "file_id": file_id,
        "status": "queued",
        "pdf_engine": settings.PDF_ENGINE,
    }
