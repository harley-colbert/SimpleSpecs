"""Headers routes."""
from __future__ import annotations

from fastapi import APIRouter

from backend.models import SectionNode, SectionSpan


headers_router = APIRouter(prefix="/headers", tags=["headers"])


def _mock_section_tree(file_id: str) -> SectionNode:
    root = SectionNode(
        section_id="root",
        file_id=file_id,
        number=None,
        title="Document Root",
        depth=0,
        children=[],
        span=SectionSpan(start_object=None, end_object=None),
    )
    intro = SectionNode(
        section_id="intro",
        file_id=file_id,
        number="1",
        title="Introduction",
        depth=1,
        children=[],
        span=SectionSpan(start_object="obj-1", end_object="obj-3"),
    )
    root.children.append(intro)
    return root


@headers_router.get("/{file_id}", response_model=SectionNode, summary="Retrieve discovered headers for a file.")
def get_headers(file_id: str) -> SectionNode:
    """Return a mock section tree for the provided file identifier."""

    return _mock_section_tree(file_id)


@headers_router.post("/{file_id}/find", response_model=SectionNode, summary="Run header discovery on a file.")
def find_headers(file_id: str) -> SectionNode:
    """Return a mock section tree while simulating header discovery."""

    return _mock_section_tree(file_id)
