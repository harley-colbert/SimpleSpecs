"""Header discovery routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from ..models import SectionNode
from ..services.headers import load_persisted_headers, run_header_discovery

headers_router = APIRouter(prefix="/headers", tags=["headers"])


@headers_router.get("/{file_id}", response_model=SectionNode)
def get_headers(file_id: str) -> SectionNode:
    """Return persisted headers for the requested file."""

    try:
        return load_persisted_headers(file_id)
    except FileNotFoundError:
        try:
            return run_header_discovery(file_id, None)
        except FileNotFoundError as exc:  # pragma: no cover - defensive
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Headers not found.",
            ) from exc


@headers_router.post("/{file_id}/find", response_model=SectionNode)
def find_headers(file_id: str, llm: str | None = Query(default=None)) -> SectionNode:
    """Run header discovery for the provided file identifier."""

    if llm is not None and llm.lower() not in {"openrouter", "llamacpp"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported llm adapter.",
        )
    try:
        return run_header_discovery(file_id, llm)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parsed objects not found.",
        ) from exc
