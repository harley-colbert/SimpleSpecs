# Phase P4 — Spec Extraction Loop
**Outcome:** Per-leaf mechanical specs extracted via LLM; provenance kept; exports consistent.

## Tasks
1. Iterate leaf sections only; prompt includes section number/title and text.
2. Retries/backoff; resumable progress; max concurrency limiter.
3. Normalize bullets; dedup globally per file; fill `source_object_ids` minimal cover.
4. `POST /specs/{file_id}/find` runs loop; `GET /specs/{file_id}` returns table.
5. Frontend progress + CSV/JSON export.

## Acceptance
- Idempotency across runs; deterministic table order.
