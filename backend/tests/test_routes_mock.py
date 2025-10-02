"""Tests for mock API endpoints."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from backend.main import create_app

client = TestClient(create_app())


def test_routes_mock() -> None:
    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    ingest = client.post("/ingest")
    assert ingest.status_code == 200
    ingest_payload = ingest.json()
    assert ingest_payload["status"] == "queued"
    assert "file_id" in ingest_payload

    file_id = ingest_payload["file_id"]
    parsed = client.get(f"/parsed/{file_id}")
    assert parsed.status_code == 200
    assert isinstance(parsed.json(), list)

    chunks = client.post(f"/chunks/{file_id}")
    assert chunks.status_code == 200
    assert "section-intro" in chunks.json()

    headers = client.get(f"/headers/{file_id}")
    assert headers.status_code == 200
    assert headers.json()["title"] == "Document"

    specs = client.get(f"/specs/{file_id}")
    assert specs.status_code == 200
    assert len(specs.json()) >= 1
