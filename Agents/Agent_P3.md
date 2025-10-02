# Agent — Phase 3: Granular Chunking by Section
**Date:** 2025-10-02

## Read these inputs first (do not proceed until read completely)
- `plan_docs/overview.md`
- `plan_docs/phase_P3_*.md`
- `finalstubs/finalstubs_latest.json`
- `finalstubs/finalstubs_P3.json`

## Goal
Implement **Phase P3** exactly as specified. Create/modify only files listed in `finalstubs_P3.json`. All code must be importable and runnable. Follow PEP 8 and use type hints.

## What to build
- Implement granular chunking in `backend/services/chunker.py`: leaves→single chunk; parents=ordered union.
- `POST /chunks/{file_id}` computes/persists mapping.
- Frontend previews for each section in `ui-sections.js`.

## Acceptance criteria
- Synthetic doc tests validate exact boundaries (`test_chunker.py`).
- Parent aggregation equals ordered union of descendants (`test_parent_aggregation.py`).

## Hard rules
- Only touch files listed for P3 in `finalstubs_P3.json`.
- Preserve file paths and exported symbols exactly.
- Write deterministic unit tests where specified and make them pass.
- Keep the app **UNO-less** and ensure `Settings.PDF_ENGINE` (`native|mineru|auto`) remains intact across phases.
- Use mocks for external services unless the phase explicitly implements them.

## Deliverables
1. List of created/modified files.
2. Commands to run the app/tests.
3. Sample JSON responses for one representative endpoint.

