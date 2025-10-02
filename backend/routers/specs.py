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
            file_id=file_id,
            section_id=f"{file_id}-sec-1",
            section_number="1",
            section_title="Power Requirements",
            spec_text="System shall operate on 120V AC.",
            confidence=0.95,
            source_object_ids=[f"{file_id}-obj-1"],
        ),
        SpecItem(
            spec_id=f"{file_id}-spec-2",
            file_id=file_id,
            section_id=f"{file_id}-sec-2",
            section_number="2",
            section_title="Environmental Limits",
            spec_text="Operating temperature range 0-50C.",
            confidence=0.6,
            source_object_ids=[f"{file_id}-obj-2"],
        ),
    ]
