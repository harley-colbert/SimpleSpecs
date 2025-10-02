from __future__ import annotations

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("fitz")

import fitz  # type: ignore  # noqa: E402

from backend.services.pdf_native import NativePdfParser


def test_native_pdf_parser_returns_text(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello Native PDF Parser")
    doc.save(pdf_path)

    parser = NativePdfParser()
    objects = parser.parse_pdf(str(pdf_path))

    assert objects, "Expected parsed objects"
    first_text = next((obj for obj in objects if obj.kind == "text"), None)
    assert first_text is not None
    assert first_text.text is not None
    assert "Hello Native" in first_text.text
