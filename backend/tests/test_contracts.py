"""Contract tests for Pydantic models."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.models import BoundingBox, ParsedObject, SectionNode, SpecItem


def test_models_schema() -> None:
    bbox = BoundingBox(x0=0, y0=0, x1=10, y1=10)
    parsed = ParsedObject(
        object_id="file-obj-1",
        file_id="file",
        kind="text",
        text="example",
        page_index=0,
        bbox=bbox,
    )
    section = SectionNode(
        section_id="sec-root",
        title="Root",
        level=0,
        children=[
            SectionNode(section_id="sec-child", title="Child", level=1, object_ids=[parsed.object_id])
        ],
    )
    spec = SpecItem(
        spec_id="spec-1",
        section_id=section.section_id,
        title="Requirement",
        content="System shall be mockable.",
    )

    assert parsed.kind == "text"
    assert section.children[0].object_ids == [parsed.object_id]
    assert spec.status == "draft"
    assert parsed.model_dump()["bbox"]["x1"] == 10
