"""File-related routes."""
from __future__ import annotations

from fastapi import APIRouter

from backend.models import MockFileSummary, ParsedObject, SectionNode, SectionSpan, SpecItem


files_router = APIRouter(tags=["files"])


def _mock_parsed_objects(file_id: str) -> list[ParsedObject]:
    return [
        ParsedObject(
            object_id="obj-1",
            file_id=file_id,
            kind="text",
            text="Mock paragraph content.",
            page_index=0,
            bbox=[0.0, 0.0, 100.0, 50.0],
            order_index=0,
            metadata={"source": "mock"},
        )
    ]


def _mock_sections(file_id: str) -> list[SectionNode]:
    root = SectionNode(
        section_id="root",
        file_id=file_id,
        number=None,
        title="Document Root",
        depth=0,
        children=[],
        span=SectionSpan(start_object="obj-1", end_object="obj-1"),
    )
    return [root]


def _mock_specs(file_id: str) -> list[SpecItem]:
    return [
        SpecItem(
            spec_id="spec-1",
            file_id=file_id,
            section_id="root",
            section_number=None,
            section_title="Document Root",
            spec_text="Mock specification for demonstration.",
            confidence=None,
            source_object_ids=["obj-1"],
        )
    ]


@files_router.get("/parsed/{file_id}", response_model=list[ParsedObject], summary="Get parsed objects for a file.")
def get_parsed_objects(file_id: str) -> list[ParsedObject]:
    """Return mock parsed objects for a file."""

    return _mock_parsed_objects(file_id)


@files_router.post("/chunks/{file_id}", summary="Create chunk assignments for a file.")
def create_chunks(file_id: str) -> dict[str, list[str]]:
    """Return a mapping of section ids to parsed object ids."""

    return {"root": [obj.object_id for obj in _mock_parsed_objects(file_id)]}


@files_router.get("/files/{file_id}", response_model=MockFileSummary, summary="Summarise file processing state.")
def get_file_summary(file_id: str) -> MockFileSummary:
    """Return a combined summary of the mock processing state."""

    return MockFileSummary(
        file_id=file_id,
        parsed_objects=_mock_parsed_objects(file_id),
        sections=_mock_sections(file_id),
        specs=_mock_specs(file_id),
        pdf_engine="native",
    )
