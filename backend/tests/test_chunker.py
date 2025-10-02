"""Unit tests for the chunking helpers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.models import ParsedObject, SectionNode, SectionSpan
from backend.services.chunker import compute_section_spans


def _make_object(file_id: str, index: int, text: str) -> ParsedObject:
    return ParsedObject(
        object_id=f"{file_id}-obj-{index}",
        file_id=file_id,
        kind="text",
        text=text,
        page_index=0,
        bbox=None,
        order_index=index,
    )


def test_compute_section_spans() -> None:
    """Objects are deterministically partitioned across section leaves."""

    file_id = "file"
    objects = [
        _make_object(file_id, 0, "Heading"),
        _make_object(file_id, 1, "Details 1"),
        _make_object(file_id, 2, "Details 2"),
        _make_object(file_id, 3, "Details 3"),
        _make_object(file_id, 4, "Details 4"),
    ]

    section_alpha = SectionNode(
        section_id="sec-alpha",
        file_id=file_id,
        title="Alpha",
        depth=1,
        children=[],
        span=SectionSpan(
            start_object=objects[0].object_id,
            end_object=objects[1].object_id,
        ),
    )
    section_beta = SectionNode(
        section_id="sec-beta",
        file_id=file_id,
        title="Beta",
        depth=2,
        children=[],
        span=SectionSpan(
            start_object=objects[0].object_id,
            end_object=objects[4].object_id,
        ),
    )
    section_delta = SectionNode(
        section_id="sec-delta",
        file_id=file_id,
        title="Delta",
        depth=2,
        children=[],
        span=SectionSpan(
            start_object=objects[2].object_id,
            end_object=objects[4].object_id,
        ),
    )
    section_gamma = SectionNode(
        section_id="sec-gamma",
        file_id=file_id,
        title="Gamma",
        depth=1,
        children=[],
        span=SectionSpan(
            start_object=objects[0].object_id,
            end_object=objects[4].object_id,
        ),
    )
    section_parent = SectionNode(
        section_id="sec-parent",
        file_id=file_id,
        title="Parent",
        depth=1,
        children=[section_beta, section_delta],
    )
    root = SectionNode(
        section_id="root",
        file_id=file_id,
        title="Document",
        depth=0,
        children=[section_alpha, section_gamma, section_parent],
    )

    mapping = compute_section_spans(root, objects)

    assert mapping["sec-alpha"] == [objects[0].object_id, objects[1].object_id]
    assert mapping["sec-delta"] == [
        objects[2].object_id,
        objects[3].object_id,
        objects[4].object_id,
    ]
    assert mapping["sec-gamma"] == []
    assert mapping["sec-beta"] == []
    assert mapping["sec-parent"] == mapping["sec-delta"]
    assert mapping["root"] == [obj.object_id for obj in objects]
    assert set(mapping.keys()) == {
        "root",
        "sec-alpha",
        "sec-beta",
        "sec-delta",
        "sec-gamma",
        "sec-parent",
    }
