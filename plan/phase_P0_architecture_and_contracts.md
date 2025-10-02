# Phase P0 — Architecture & Contracts (UNO‑less + MinerU toggle)
**Outcome:** Frozen contracts, endpoints, adapters; config flag for PDF engine; mocks for both engines.

## Tasks
1. Add `PDF_ENGINE` config: `"native" | "mineru" | "auto"` with default `"native"`.
2. Define `PdfParser` interface with `parse_pdf(file_path) -> list[ParsedObject]`.
3. Create adapters:
   - `NativePdfParser` (pdfplumber/pdfminer.six/PyMuPDF/pikepdf + Camelot/Tabula).
   - `MinerUPdfParser` (MinerU JSON→ParsedObject normalizer).
4. Router scaffolds & mock responses for ingest, parsed, headers, chunks, specs.
5. `/system/capabilities` endpoint: detect presence of `tesseract`, `gs`, `java`, and MinerU package import.
6. Pydantic models and OpenAPI schemas; logging and error envelope.

## Acceptance
- `GET /openapi.json` exposes all endpoints.
- Switching `PDF_ENGINE` changes which parser is invoked (mocked).