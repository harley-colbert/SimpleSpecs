# Agent — Phase 4: Spec Extraction Loop
**Date:** 2025-10-02

## Read these inputs first (do not proceed until read completely)
- `plan_docs/overview.md`
- `plan_docs/phase_P4_*.md`
- `finalstubs/finalstubs_latest.json`
- `finalstubs/finalstubs_P4.json`

## Goal
Implement **Phase P4** exactly as specified. Create/modify only files listed in `finalstubs_P4.json`. All code must be importable and runnable. Follow PEP 8 and use type hints.

## What to build
- Implement spec extraction loop in `backend/services/specs.py`:
  - Iterate leaf sections; per-section prompt (include section number/title + text).
  - Retries/backoff; resumable progress; concurrency limiter.
  - Normalize bullets; deduplicate; fill `source_object_ids` minimal cover.
- Routes: `POST /specs/{file_id}/find`, `GET /specs/{file_id}`.
- Frontend: progress and results table in `ui-specs.js`; CSV/JSON export control.

## Acceptance criteria
- Idempotent runs yield identical `SpecItem[]`.
- Failure injection test: loop resumes and completes (`test_specs_loop_resume.py`).
- Merge/dedup rules validated (`test_specs_merge.py`).

## Hard rules
- Only touch files listed for P4 in `finalstubs_P4.json`.
- Preserve file paths and exported symbols exactly.
- Write deterministic unit tests where specified and make them pass.
- Keep the app **UNO-less** and ensure `Settings.PDF_ENGINE` (`native|mineru|auto`) remains intact across phases.
- Use mocks for external services unless the phase explicitly implements them.

## Deliverables
1. List of created/modified files.
2. Commands to run the app/tests.
3. Sample JSON responses for one representative endpoint.

