# Agent — Phase 5: QA, Export & Packaging
**Date:** 2025-10-02

## Read these inputs first (do not proceed until read completely)
- `plan_docs/overview.md`
- `plan_docs/phase_P5_*.md`
- `finalstubs/finalstubs_latest.json`
- `finalstubs/finalstubs_P5.json`

## Goal
Implement **Phase P5** exactly as specified. Create/modify only files listed in `finalstubs_P5.json`. All code must be importable and runnable. Follow PEP 8 and use type hints.

## What to build
- Implement `GET /export/{file_id}?fmt=csv|json` with exact schema + encoding guarantees.
- Add parity/coverage tests between native and MinerU outputs (`test_pdf_parity.py`) if not already robust.
- Surface `/system/capabilities` info in the UI (optional).
- CI: ensure tests and coverage (>=80%) pass reliably.

## Acceptance criteria
- Full demo runs under `native`, `mineru`, and `auto` without code changes.
- `test_export_csv_json.py` passes; coverage threshold met.

## Hard rules
- Only touch files listed for P5 in `finalstubs_P5.json`.
- Preserve file paths and exported symbols exactly.
- Write deterministic unit tests where specified and make them pass.
- Keep the app **UNO-less** and ensure `Settings.PDF_ENGINE` (`native|mineru|auto`) remains intact across phases.
- Use mocks for external services unless the phase explicitly implements them.

## Deliverables
1. List of created/modified files.
2. Commands to run the app/tests.
3. Sample JSON responses for one representative endpoint.

