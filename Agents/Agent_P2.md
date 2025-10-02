# Agent — Phase 2: Header Discovery (LLM)
**Date:** 2025-10-02

## Read these inputs first (do not proceed until read completely)
- `plan_docs/overview.md`
- `plan_docs/phase_P2_*.md`
- `finalstubs/finalstubs_latest.json`
- `finalstubs/finalstubs_P2.json`

## Goal
Implement **Phase P2** exactly as specified. Create/modify only files listed in `finalstubs_P2.json`. All code must be importable and runnable. Follow PEP 8 and use type hints.

## What to build
- Implement header discovery via LLM adapters (mock transport acceptable if not wired yet).
- Build headers prompt; handle truncation warning if text exceeds token budget.
- Implement nested-list parsing into `SectionNode` tree (`parse_nested_list_to_tree`).
- Routes: `POST /headers/{file_id}/find` and `GET /headers/{file_id}`.
- Frontend tree view in `frontend/js/ui-sections.js`.

## Acceptance criteria
- For fixture docs, displayed section tree matches LLM response semantics (numbering/title/depth).
- Unit tests pass: `test_headers_parse.py` covers bullet/numbered variants and invariants.

## Hard rules
- Only touch files listed for P2 in `finalstubs_P2.json`.
- Preserve file paths and exported symbols exactly.
- Write deterministic unit tests where specified and make them pass.
- Keep the app **UNO-less** and ensure `Settings.PDF_ENGINE` (`native|mineru|auto`) remains intact across phases.
- Use mocks for external services unless the phase explicitly implements them.

## Deliverables
1. List of created/modified files.
2. Commands to run the app/tests.
3. Sample JSON responses for one representative endpoint.

