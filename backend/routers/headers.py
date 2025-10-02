"""Mock header routes for Phase P0."""
from __future__ import annotations

from fastapi import APIRouter

from ..models import SectionNode, SectionSpan

headers_router = APIRouter(prefix="/headers", tags=["headers"])


@headers_router.get("/{file_id}", response_model=SectionNode)
def get_headers(file_id: str) -> SectionNode:
    """Return a deterministic mock header tree for the file."""

    return SectionNode(
        section_id=f"{file_id}-root",
        file_id=file_id,
        title="Document",
        depth=0,
        children=[
            SectionNode(
                section_id=f"{file_id}-sec-1",
                file_id=file_id,
                number="1",
                title="Introduction",
                depth=1,
                span=SectionSpan(
                    start_object=f"{file_id}-obj-1",
                    end_object=f"{file_id}-obj-1",
                ),
            ),
            SectionNode(
                section_id=f"{file_id}-sec-2",
                file_id=file_id,
                number="2",
                title="Details",
                depth=1,
                span=SectionSpan(
                    start_object=f"{file_id}-obj-2",
                    end_object=f"{file_id}-obj-2",
                ),
            ),
        ],
    )
