"""Mock specification routes for Phase P0."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter

from ..models import SpecItem

specs_router = APIRouter(prefix="/specs", tags=["specs"])


@specs_router.get("/{file_id}", response_model=List[SpecItem])
def get_spec_items(file_id: str) -> List[SpecItem]:
    """Return deterministic mock specification items for the file."""

    return [
        SpecItem(
            spec_id=f"{file_id}-spec-1",
            section_id=f"{file_id}-sec-1",
            title="Power Requirements",
            content="System shall operate on 120V AC.",
            status="confirmed",
            confidence=0.95,
        ),
        SpecItem(
            spec_id=f"{file_id}-spec-2",
            section_id=f"{file_id}-sec-2",
            title="Environmental Limits",
            content="Operating temperature range 0-50C.",
            status="draft",
            confidence=0.6,
        ),
    ]
