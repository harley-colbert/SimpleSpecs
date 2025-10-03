"""Headers extraction endpoint."""
from __future__ import annotations

import re
from typing import List

from fastapi import APIRouter, HTTPException

from ..models import HeaderItem, HeadersRequest
from ..services.llm import get_provider
from ..services.text_blocks import document_text
from ..store import headers_path, read_jsonl, upload_objects_path, write_json

router = APIRouter(prefix="/api")

_HEADERS_PROMPT = """Please show a simple numbered nested list of all headers and subheaders for this document.
Return ONLY the list enclosed in #headers# fencing, like:

#headers#
1. Top Level
   1.1 Sub
      1.1.1 Sub-sub
2. Another Top
#headers#
"""


@router.post("/headers", response_model=list[HeaderItem])
async def extract_headers(payload: HeadersRequest) -> List[HeaderItem]:
    objects_raw = read_jsonl(upload_objects_path(payload.upload_id))
    if not objects_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    document = document_text(objects_raw)
    if not document.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document is empty")

    provider = get_provider(
        payload.provider,
        model=payload.model,
        params=payload.params,
        api_key=payload.api_key,
        base_url=payload.base_url,
    )
    messages = [
        {"role": "system", "content": "You analyze engineering specification documents."},
        {
            "role": "user",
            "content": f"{_HEADERS_PROMPT}\n\nDocument contents:\n{document}",
        },
    ]
    response_text = await provider.chat(messages)
    match = re.search(r"#headers#(.*?)#headers#", response_text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM returned unexpected format")

    content = match.group(1)
    headers: list[HeaderItem] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match_line = re.match(r"^(\d+(?:\.\d+)*)[\s\-\.]+(.+)$", line)
        if not match_line:
            continue
        section_number = match_line.group(1).strip()
        section_name = match_line.group(2).strip()
        headers.append(HeaderItem(section_number=section_number, section_name=section_name))

    if not headers:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No headers parsed")

    write_json(headers_path(payload.upload_id), [header.model_dump() for header in headers])
    return headers
