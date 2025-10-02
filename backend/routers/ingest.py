"""Mock ingest routes for Phase P0."""
from __future__ import annotations

import uuid

from fastapi import APIRouter

from ..config import get_settings

ingest_router = APIRouter(prefix="/ingest", tags=["ingest"])


@ingest_router.post("", summary="Queue a file for ingestion")
def queue_ingest() -> dict[str, str]:
    """Return a deterministic mock ingest response."""

    settings = get_settings()
    file_id = uuid.uuid5(uuid.NAMESPACE_URL, "simplespecs/mock").hex[:8]
    return {
        "file_id": file_id,
        "status": "queued",
        "pdf_engine": settings.PDF_ENGINE,
    }
