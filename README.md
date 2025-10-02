# SimpleSpecs — Phase P0

Phase P0 establishes the project structure, configuration contracts, and mock endpoints for the UNO-less parsing stack with an optional MinerU toggle.

## Prerequisites
- Python 3.12+

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn sqlmodel pydantic pydantic-settings httpx
```

## Running the API
```bash
uvicorn backend.main:create_app --factory --host 127.0.0.1 --port 8000
```

Then open [http://127.0.0.1:8000/frontend/](http://127.0.0.1:8000/frontend/) to view the scaffolded UI.

## Configuration
Set environment variables to override defaults:
- `PDF_ENGINE` — `native`, `mineru`, or `auto`
- `MINERU_ENABLED` — enables MinerU integration when set to `true`
- `MINERU_MODEL_OPTS` — JSON-encoded options for MinerU models

## Tests
```bash
pytest -q
```
