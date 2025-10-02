from __future__ import annotations

from backend.services.parse_txt import parse_txt


def test_parse_txt_lines(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("line1\nline2", encoding="utf-8")

    objects = parse_txt(str(file_path))

    assert len(objects) == 2
    assert objects[0].text == "line1"
    assert objects[0].page_index == 0
