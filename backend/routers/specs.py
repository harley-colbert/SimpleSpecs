"""Specification routes."""
from __future__ import annotations

from fastapi import APIRouter

from backend.models import SpecItem


specs_router = APIRouter(prefix="/specs", tags=["specs"])


def _mock_spec_items(file_id: str) -> list[SpecItem]:
    return [
        SpecItem(
            spec_id="spec-1",
            file_id=file_id,
            section_id="intro",
            section_number="1",
            section_title="Introduction",
            spec_text="The system shall provide a mock specification item.",
            confidence=0.75,
            source_object_ids=["obj-2"],
        )
    ]


@specs_router.get("/{file_id}", response_model=list[SpecItem], summary="Retrieve stored specification items.")
def get_specs(file_id: str) -> list[SpecItem]:
    """Return mock specification items for the provided file."""

    return _mock_spec_items(file_id)


@specs_router.post("/{file_id}/find", response_model=list[SpecItem], summary="Run spec discovery on a file.")
def find_specs(file_id: str) -> list[SpecItem]:
    """Return mock specification items while simulating discovery."""

    return _mock_spec_items(file_id)
