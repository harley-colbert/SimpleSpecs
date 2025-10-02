"""Mock file routes for Phase P0."""
from __future__ import annotations

from typing import Dict, List, Literal, Tuple

from fastapi import APIRouter

from ..models import ParsedObject

files_router = APIRouter(prefix="", tags=["files"])


def _mock_objects(file_id: str) -> List[ParsedObject]:
    """Return a deterministic set of parsed objects for a file."""

    objects: List[ParsedObject] = []
    samples: List[Tuple[Literal["text", "table", "image"], str, int, List[float]]] = [
        (
            "text",
            "Sample introduction paragraph.",
            0,
            [12.0, 48.0, 580.0, 680.0],
        ),
        (
            "table",
            "Table describing requirements.",
            1,
            [36.0, 120.0, 560.0, 420.0],
        ),
    ]

    for order, (kind, text, page_index, bbox) in enumerate(samples):
        objects.append(
            ParsedObject(
                object_id=f"{file_id}-obj-{order + 1}",
                file_id=file_id,
                kind=kind,
                text=text,
                page_index=page_index,
                bbox=bbox,
                order_index=order,
            )
        )

    return objects


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
