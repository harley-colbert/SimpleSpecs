"""Tests for system capability reporting."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import create_app  # noqa: E402


client = TestClient(create_app())


def test_capabilities_endpoint() -> None:
    """Detect optional tools and MinerU availability."""

    response = client.get("/system/capabilities")
    assert response.status_code == 200
    data = response.json()
    for key in {"tesseract", "ghostscript", "java", "mineru_importable"}:
        assert key in data
        assert isinstance(data[key], bool)
