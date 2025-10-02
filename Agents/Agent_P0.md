# Agent — Phase 0: Architecture & Contracts (UNO-less + MinerU toggle)
**Date:** 2025-10-02

## Read these inputs first (do not proceed until read completely)
- `plan_docs/overview.md`
- `plan_docs/phase_P0_*.md`
- `finalstubs/finalstubs_latest.json`
- `finalstubs/finalstubs_P0.json`

## Goal
Implement **Phase P0** exactly as specified. Create/modify only files listed in `finalstubs_P0.json`. All code must be importable and runnable. Follow PEP 8 and use type hints.

## What to build
- FastAPI app skeleton with routers and mocks:
  - `backend/main.py` with `create_app()` factory, CORS, `/healthz`.
  - Routers: `backend/routers/ingest.py`, `headers.py`, `specs.py`, `files.py`, `system.py` (mock payloads).
- Config: `backend/config.py` with `PDF_ENGINE` (`native|mineru|auto`), `MINERU_ENABLED`, `MINERU_MODEL_OPTS`.
- Models: `ParsedObject`, `SectionNode`, `SpecItem` in `backend/models.py` (Pydantic v2).
- Store scaffold: `backend/store.py` with `get_session()` and engine init (no real tables yet).
- Logging setup: `backend/logging.py` (`setup_logging()`).
- LLM protocol: `backend/services/llm_client.py` (protocol + empty adapters).
- PDF parser protocol/selector stub: `backend/services/pdf_parser.py`.
- Frontend scaffold: `frontend/index.html`, `frontend/js/api.js`, `frontend/js/state.js`.
- Runners: `run.py`, `run_local.py`.
- Tests (mock level): `backend/tests/test_contracts.py`, `test_routes_mock.py`, `test_system_capabilities.py`.
- `/system/capabilities` route checks: `tesseract`, `gs`, `java`, and MinerU importability (best-effort).

## Acceptance criteria
- `GET /openapi.json` returns the schema.
- `GET /healthz` returns `{"status":"ok"}`.
- `/system/capabilities` returns booleans for tools and `mineru_importable`.
- All tests in `backend/tests/` pass (mock level).

## Hard rules
- Only touch files listed for P0 in `finalstubs_P0.json`.
- Preserve file paths and exported symbols exactly.
- Write deterministic unit tests where specified and make them pass.
- Keep the app **UNO-less** and ensure `Settings.PDF_ENGINE` (`native|mineru|auto`) remains intact across phases.
- Use mocks for external services unless the phase explicitly implements them.

## Deliverables
1. List of created/modified files.
2. Commands to run the app/tests.
3. Sample JSON responses for one representative endpoint.

