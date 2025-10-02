"""Contract tests ensuring model structures remain stable."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.models import ParsedObject, SectionNode, SectionSpan, SpecItem  # noqa: E402


def test_models_schema() -> None:
    """Instantiate models and ensure nested defaults behave as expected."""

    parsed = ParsedObject(
        object_id="obj-1",
        file_id="file-1",
        kind="text",
        text="Example",
        page_index=0,
        bbox=[0.0, 0.0, 10.0, 10.0],
        order_index=1,
        metadata={"source": "test"},
    )

    section = SectionNode(
        section_id="root",
        file_id="file-1",
        number=None,
        title="Root",
        depth=0,
        children=[
            SectionNode(
                section_id="child",
                file_id="file-1",
                number="1",
                title="Child",
                depth=1,
                children=[],
                span=SectionSpan(start_object="obj-1", end_object="obj-1"),
            )
        ],
        span=SectionSpan(start_object="obj-1", end_object="obj-1"),
    )

    spec = SpecItem(
        spec_id="spec-1",
        file_id="file-1",
        section_id="root",
        section_number="1",
        section_title="Root",
        spec_text="Must support mock data",
        confidence=0.5,
        source_object_ids=[parsed.object_id],
    )

    assert parsed.object_id == "obj-1"
    assert section.children[0].title == "Child"
    assert spec.source_object_ids == ["obj-1"]
