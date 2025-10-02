"""Mock file routes for Phase P0."""
from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ..models import ParsedObject

files_router = APIRouter(prefix="", tags=["files"])


def _mock_objects(file_id: str) -> List[ParsedObject]:
    """Return a deterministic set of parsed objects for a file."""

    return [
        ParsedObject(
            object_id=f"{file_id}-obj-1",
            file_id=file_id,
            kind="text",
            text="Sample introduction paragraph.",
            page_index=0,
        ),
        ParsedObject(
            object_id=f"{file_id}-obj-2",
            file_id=file_id,
            kind="table",
            text="Table describing requirements.",
            page_index=1,
        ),
    ]


@files_router.get("/parsed/{file_id}", response_model=List[ParsedObject])
def get_parsed_objects(file_id: str) -> List[ParsedObject]:
    """Return mock parsed objects for the provided file ID."""

    return _mock_objects(file_id)


@files_router.post("/chunks/{file_id}")
def get_chunks(file_id: str) -> Dict[str, List[str]]:
    """Return a deterministic mapping of section IDs to object IDs."""

    objects = _mock_objects(file_id)
    return {
        "section-intro": [objects[0].object_id],
        "section-details": [obj.object_id for obj in objects[1:]],
    }


@files_router.get("/files/{file_id}")
def get_file_summary(file_id: str) -> Dict[str, str | int]:
    """Return a minimal mock summary for the file."""

    objects = _mock_objects(file_id)
    return {
        "file_id": file_id,
        "filename": f"{file_id}.pdf",
        "object_count": len(objects),
    }
