"""File-related routes that complement ingestion."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..services.chunker import load_persisted_chunks, run_chunking

files_router = APIRouter(prefix="", tags=["files"])


@files_router.post("/chunks/{file_id}", response_model=dict[str, list[str]])
def create_chunks(file_id: str) -> dict[str, list[str]]:
    """Compute and persist section chunks for the provided file."""

    try:
        return run_chunking(file_id)
    except FileNotFoundError as exc:
        detail = str(exc) or "Required artifacts missing."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from exc


@files_router.get("/chunks/{file_id}", response_model=dict[str, list[str]])
def get_chunks(file_id: str) -> dict[str, list[str]]:
    """Return persisted section chunks for the provided file."""

    try:
        return load_persisted_chunks(file_id)
    except FileNotFoundError as exc:
        detail = str(exc) or "Chunks not found."
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from exc
