"""Headers extraction endpoint."""
from __future__ import annotations

import re
from typing import List

from fastapi import APIRouter, HTTPException

from ..models import HeaderItem, HeadersRequest
from ..services.documents import get_document_or_404, get_step, upsert_step
from ..services.llm import get_provider
from ..services.text_blocks import document_text

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
    document = get_document_or_404(payload.upload_id)

    existing_step = get_step(payload.upload_id, "headers")
    if (
        existing_step
        and existing_step.status == "completed"
        and existing_step.result is not None
    ):
        return [HeaderItem.model_validate(item) for item in existing_step.result]

    objects_raw = document.parsed_objects or []
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

    upsert_step(
        payload.upload_id,
        name="headers",
        result=[header.model_dump() for header in headers],
        provider=payload.provider,
        model=payload.model,
        params=payload.params,
        base_url=payload.base_url,
        api_key_used=bool(payload.api_key),
    )
    return headers
