from __future__ import annotations

import pytest

pytest.importorskip("docx")

from docx import Document  # type: ignore  # noqa: E402

from backend.services.parse_docx import parse_docx


def test_parse_docx_basic(tmp_path):
    file_path = tmp_path / "sample.docx"
    document = Document()
    document.add_paragraph("Hello DOCX parser")
    table = document.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "A"
    table.rows[0].cells[1].text = "B"
    document.save(file_path)

    objects = parse_docx(str(file_path))

    kinds = {obj.kind for obj in objects}
    assert "text" in kinds
    assert "table" in kinds
