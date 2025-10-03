"""Export endpoints."""
from __future__ import annotations

import csv
import io

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..services.documents import get_step

router = APIRouter(prefix="/api")


@router.get("/export/specs.csv")
async def export_specs(upload_id: str = Query(...)) -> StreamingResponse:
    step = get_step(upload_id, "specs")
    if not step or step.result is None:
        raise HTTPException(status_code=404, detail="No specifications available")

    specs = step.result

    header = ["Section number", "Section name", "Specification", "Domain"]
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    for item in specs:
        row = [
            (item.get("section_number") or "").replace("\r", " ").replace("\n", " "),
            (item.get("section_name") or "").replace("\r", " ").replace("\n", " "),
            (item.get("specification") or "").replace("\r", " ").replace("\n", " "),
            (item.get("domain") or "").replace("\r", " ").replace("\n", " "),
        ]
        writer.writerow(row)
    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=specs.csv"}
    return StreamingResponse(buffer, media_type="text/csv", headers=headers)
