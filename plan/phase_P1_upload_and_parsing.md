# Phase P1 — Upload & Parsing (UNO‑less with MinerU option)
**Outcome:** Deterministic extraction to `ParsedObject[]` using the selected engine; DOCX/TXT native; OCR optional.

## Tasks
1. Implement `POST /ingest`: save to `artifacts/{file_id}/source` and register file.
2. Implement `NativePdfParser`:
   - pdfplumber → text objs with bbox/page/order
   - pikepdf → doc metadata, attachments
   - PyMuPDF → images (coords, DPI) and vector objects
   - Camelot/Tabula (select at runtime) for tables
3. Implement `MinerUPdfParser`:
   - Call MinerU pipeline; map its JSON to `ParsedObject[]`.
   - Preserve page/bbox if available; create stable `order_index`.
4. Implement selection logic:
   - `PDF_ENGINE=native|mineru|auto`
   - For `auto`, run native; if heuristics fail thresholds, switch to MinerU (and tag provenance).
5. DOCX: `python-docx` + tables; mammoth as structural cross-check; docx2python for table-heavy.
6. TXT: encoding detection; line objects with synthetic bbox=None, page=0.
7. OCR (optional): if scanned PDF and MinerU unavailable, run `ocrmypdf` to add text layer, then re-run native.
8. `GET /parsed/{file_id}` returns `ParsedObject[]`.

## Acceptance
- On fixtures, both `native` and `mineru` modes produce comprehensive coverage; parity tests pass with tolerances.
- Error paths and limits (size/type) return clear messages.
