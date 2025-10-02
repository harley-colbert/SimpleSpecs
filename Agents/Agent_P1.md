# Agent — Phase 1: Upload & Parsing (Native + MinerU)
**Date:** 2025-10-02

## Read these inputs first (do not proceed until read completely)
- `plan_docs/overview.md`
- `plan_docs/phase_P1_*.md`
- `finalstubs/finalstubs_latest.json`
- `finalstubs/finalstubs_P1.json`

## Goal
Implement **Phase P1** exactly as specified. Create/modify only files listed in `finalstubs_P1.json`. All code must be importable and runnable. Follow PEP 8 and use type hints.

## What to build
- Implement `NativePdfParser` in `backend/services/pdf_native.py` using pdfplumber+PyMuPDF+pikepdf (+ Camelot/Tabula).
- Implement `MinerUPdfParser` in `backend/services/pdf_mineru.py` mapping MinerU JSON→ParsedObject.
- Implement selection logic in `backend/services/pdf_parser.py` (`select_pdf_parser`) honoring `PDF_ENGINE` and AUTO heuristics.
- Implement `POST /ingest` (save original file under `artifacts/<file_id>/source`).
- Implement `GET /parsed/{file_id}` returning `ParsedObject[]` from DB or cache.
- DOCX parser in `backend/services/parse_docx.py` (python-docx + tables; mammoth/docx2python as needed).
- TXT parser in `backend/services/parse_txt.py` with encoding detection.
- OCR fallback path (optional runtime): if scanned and MinerU unavailable, run `ocrmypdf` then re-parse native.
- Tests: `test_parse_pdf_native.py`, `test_parse_pdf_mineru.py`, `test_pdf_parity.py`, `test_parse_docx.py`, `test_parse_txt.py`, `test_upload_limits.py`.

## Acceptance criteria
- For fixture PDFs, `native` and `mineru` produce semantically equivalent coverage (within tolerance); parity test passes.
- Upload limits enforced; correct error responses for size/type.
- ParsedObject ordering is deterministic; metadata populated (page, bbox on PDF).

## Hard rules
- Only touch files listed for P1 in `finalstubs_P1.json`.
- Preserve file paths and exported symbols exactly.
- Write deterministic unit tests where specified and make them pass.
- Keep the app **UNO-less** and ensure `Settings.PDF_ENGINE` (`native|mineru|auto`) remains intact across phases.
- Use mocks for external services unless the phase explicitly implements them.

## Deliverables
1. List of created/modified files.
2. Commands to run the app/tests.
3. Sample JSON responses for one representative endpoint.

