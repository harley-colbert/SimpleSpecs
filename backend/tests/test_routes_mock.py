"""Tests covering mock route responses."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient  # noqa: E402

from backend.main import create_app  # noqa: E402


client = TestClient(create_app())


def test_routes_mock() -> None:
    """Mock endpoints respond 200 and return expected payload shapes."""

    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    ingest = client.post("/ingest")
    assert ingest.status_code == 200
    body = ingest.json()
    assert body["status"] == "queued"
    file_id = body["file_id"]

    parsed = client.get(f"/parsed/{file_id}")
    assert parsed.status_code == 200
    assert isinstance(parsed.json(), list)

    headers = client.get(f"/headers/{file_id}")
    assert headers.status_code == 200
    assert headers.json()["title"] == "Document Root"

    specs = client.get(f"/specs/{file_id}")
    assert specs.status_code == 200
    assert len(specs.json()) >= 1

    chunks = client.post(f"/chunks/{file_id}")
    assert chunks.status_code == 200
    assert "root" in chunks.json()

    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
