# SimpleSpecs — Phase P0

Phase P0 delivers the core FastAPI skeleton, configuration contracts, and mock endpoints for the UNO-less parsing stack with an optional MinerU toggle.

## Prerequisites
- Python 3.12+

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the API
```bash
uvicorn backend.main:create_app --factory --host 127.0.0.1 --port 8000
```

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to view the scaffolded UI and [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for API documentation.

## Configuration
Settings are loaded from environment variables (prefixed with `SIMPLS_` when desired). Key options include:

- `PDF_ENGINE` — `native`, `mineru`, or `auto` (default `native`)
- `MINERU_ENABLED` — enables MinerU integrations when true (default `false`)
- `MINERU_MODEL_OPTS` — JSON/dict style mapping for MinerU models
- `ALLOW_ORIGINS` — comma-separated origins for CORS (default `*`)
- `MAX_FILE_MB` — maximum upload size (default `50`)

## Tests
```bash
pytest -q
```
