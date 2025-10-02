"""Mock header routes for Phase P0."""
from __future__ import annotations

from fastapi import APIRouter

from ..models import SectionNode

headers_router = APIRouter(prefix="/headers", tags=["headers"])


@headers_router.get("/{file_id}", response_model=SectionNode)
def get_headers(file_id: str) -> SectionNode:
    """Return a deterministic mock header tree for the file."""

    return SectionNode(
        section_id=f"{file_id}-root",
        title="Document",
        level=0,
        children=[
            SectionNode(
                section_id=f"{file_id}-sec-1",
                title="Introduction",
                level=1,
                object_ids=[f"{file_id}-obj-1"],
            ),
            SectionNode(
                section_id=f"{file_id}-sec-2",
                title="Details",
                level=1,
                object_ids=[f"{file_id}-obj-2"],
            ),
        ],
    )
