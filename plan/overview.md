# Simplespecs — UNO‑less Text Extraction Plan (with MinerU toggle)
**Date:** 2025-10-02

This plan removes any dependency on LibreOffice/UNO/pyuno and adopts a **native parsing stack** for PDF/DOCX/TXT, while introducing **MinerU** as a user‑toggleable PDF pipeline. Users can choose **Native**, **MinerU**, or **Auto** (heuristic).

## Goals
- End‑to‑end pipeline: Upload → Parse (text/tables/images + per‑object metadata) → LLM Header Discovery → Section Chunking → Per‑Section Spec Extraction → Aggregation/Export.
- Keep everything **venv‑installable via requirements.txt** (no pyuno).
- Allow a **user toggle** for the PDF engine:
  - **native** = pdfplumber/pdfminer.six/PyMuPDF(+pikepdf) with Camelot/Tabula for tables
  - **mineru** = MinerU JSON/Markdown pipeline normalized into our data model
  - **auto** = native first; fallback to MinerU on heuristics (e.g., low text density, multi‑column confusion, heavy figures, OCR need)

## Stack
- **Backend:** Python 3.12 + FastAPI, SQLModel/SQLite, httpx.
- **Frontend:** HTML/CSS + ESM JS.
- **LLMs:** OpenRouter and/or llama.cpp adapters.
- **Storage:** `artifacts/` for files; SQLite for objects/sections/specs.
- **Parsing (UNO‑less):**
  - **PDF (native):** pdfplumber, pdfminer.six, PyMuPDF, pikepdf; tables via Camelot/Tabula.
  - **PDF (MinerU):** MinerU (e.g., magic‑pdf) → JSON normalized to ParsedObject.
  - **DOCX:** python‑docx, mammoth, docx2python.
  - **TXT:** stdlib (encoding detection via chardet/charset-normalizer).
  - **OCR (optional):** ocrmypdf, pytesseract.

## Canonical Models
```ts
ParsedObject {
  object_id: string
  file_id: string
  kind: 'text' | 'table' | 'image'
  text: string | null
  page_index: number | null
  bbox: [number, number, number, number] | null
  order_index: number
  metadata: Record<string, any>
}

SectionNode {
  section_id: string
  file_id: string
  number: string | null
  title: string
  depth: number
  children: SectionNode[]
  span: { start_object: string | null, end_object: string | null }
}

SpecItem {
  spec_id: string
  file_id: string
  section_id: string
  section_number: string | null
  section_title: string
  spec_text: string
  confidence: number | null
  source_object_ids: string[]
}
```

## API Surface
- `POST /ingest` → `{file_id}`
- `GET /parsed/{file_id}` → `ParsedObject[]`
- `POST /headers/{file_id}/find` → `SectionNode` (root)
- `GET /headers/{file_id}` → `SectionNode`
- `POST /chunks/{file_id}` → `{ section_id: object_id[] }`
- `POST /specs/{file_id}/find` → `SpecItem[]`
- `GET /specs/{file_id}` → `SpecItem[]`
- `GET /export/{file_id}?fmt=csv|json`
- `GET /system/capabilities` → which optional tools are present (tesseract, ghostscript, java, mineru pkg)

## Config (UNO‑less + MinerU toggle)
`Settings.PDF_ENGINE` in `config.py`: `"native" | "mineru" | "auto"`  
`Settings.MinerU_ENABLED: bool` and `Settings.MinerU_MODEL_OPTS: dict` (if needed).

## Heuristics for AUTO
- Low text density but many images (suggests scanned) → prefer MinerU or OCRmyPDF then native.
- Multi‑column/figure‑heavy pages with weak table detection → attempt MinerU.
- If MinerU missing (package not installed), AUTO falls back to native with OCR as needed.

## Quality Gates
- Golden fixtures for both engines produce equivalent `ParsedObject[]` semantics (allowing minor bbox differences).
- Engine output parity tests (native ↔ MinerU) on sample PDFs: counts, text coverage, table presence.
- Idempotency for LLM steps and deterministic aggregation.
