"""Headers extraction endpoint."""
from __future__ import annotations

import logging
import os
import re
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, status

from ..models import HeaderItem, HeadersRequest
from ..services.llm import get_provider
from ..services.text_blocks import document_text
from ..store import headers_path, read_jsonl, upload_objects_path, write_json

router = APIRouter(prefix="/api")
log = logging.getLogger(__name__)

DEV_VERBOSE = os.getenv("DEV_VERBOSE", "0") == "1"
DOC_CHAR_LIMIT = int(os.getenv("HEADERS_DOC_CHAR_LIMIT", "120000"))  # safety cap

_HEADERS_PROMPT = """Please show a simple numbered nested list of all headers and subheaders for this document.
Return ONLY the list enclosed in #headers# fencing, like:

#headers#
1. Top Level
   1.1 Sub
      1.1.1 Sub-sub
2. Another Top
#headers#

If you cannot comply exactly, reply:
#headers#
ERROR
#headers#
""".strip()


def _redact(text: str) -> str:
    # very basic redactions; extend if you log secrets in prompts/responses
    text = re.sub(r'(sk-[A-Za-z0-9_\-]{16,})', 'sk-***REDACTED***', text)
    text = re.sub(r'("api_key"\s*:\s*")[^"]+(")', r'\1***REDACTED***\2', text)
    return text


def _snippet(text: str, limit: int = 800) -> str:
    text = (text or "").replace("\r", "")
    return text[:limit] + ("…[truncated]" if len(text) > limit else "")


@router.post("/headers", response_model=list[HeaderItem])
async def extract_headers(payload: HeadersRequest) -> List[HeaderItem]:
    corr_id = str(uuid.uuid4())

    # Load uploaded objects
    objects_raw = read_jsonl(upload_objects_path(payload.upload_id))
    if not objects_raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "UPLOAD_NOT_FOUND", "message": "Upload not found", "corr_id": corr_id},
        )

    document = document_text(objects_raw).strip()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "EMPTY_DOCUMENT", "message": "Document is empty", "corr_id": corr_id},
        )

    # Trim document to avoid massive prompts (configurable)
    doc_for_prompt = document if len(document) <= DOC_CHAR_LIMIT else document[:DOC_CHAR_LIMIT]

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
            "content": f"{_HEADERS_PROMPT}\n\nDocument contents:\n{doc_for_prompt}",
        },
    ]

    # Call LLM
    try:
        response_text = await provider.chat(messages)
    except Exception as e:
        log.exception("LLM call failed | corr_id=%s", corr_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "error": "LLM_CALL_FAILED",
                "message": f"{type(e).__name__}: {e}",
                "corr_id": corr_id,
            },
        ) from e

    # Log full raw (redacted) to server logs for debugging
    log.debug("LLM raw response | corr_id=%s | body=%s", corr_id, _redact(response_text))

    # Parse fenced block
    m = re.search(r"#headers#(.*?)#headers#", response_text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "LLM_UNEXPECTED_FORMAT",
                "message": "Expected a single #headers# fenced block.",
                "corr_id": corr_id,
                "snippet": _snippet(_redact(response_text)) if DEV_VERBOSE else "Enable DEV_VERBOSE=1 to see a snippet.",
                "hint": "Ensure the model returns only one fenced block: #headers# ... #headers#",
            },
        )

    content = m.group(1).strip()

    # Special deterministic failure path from prompt
    if re.fullmatch(r"ERROR", content, flags=re.IGNORECASE):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "LLM_DECLINED",
                "message": "Model indicated it could not produce the fenced list.",
                "corr_id": corr_id,
                "fenced_snippet": _snippet(content) if DEV_VERBOSE else "Enable DEV_VERBOSE=1 to see a snippet.",
            },
        )

    # Line-by-line parse (flat list with section_number + section_name)
    headers: list[HeaderItem] = []
    problems: list[str] = []
    for idx, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        # Accept forms like:
        # 1. Title
        # 1 Title
        # 1- Title
        # 1.2.3 Title
        match_line = re.match(r"^(\d+(?:\.\d+)*)[\s\-\.\)]{1,3}(.+?)\s*$", line)
        if not match_line:
            # keep note for debugging but don't fail the whole request
            problems.append(f"Unparsed line {idx}: {line!r}")
            continue

        section_number = match_line.group(1).strip()
        section_name = match_line.group(2).strip()
        headers.append(HeaderItem(section_number=section_number, section_name=section_name))

    if not headers:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "NO_HEADERS_PARSED",
                "message": "No headers matched the expected numbered format.",
                "corr_id": corr_id,
                "fenced_snippet": _snippet(content) if DEV_VERBOSE else "Enable DEV_VERBOSE=1 to see a snippet.",
                "notes": problems[:10],  # show a few hints
            },
        )

    # Persist result
    try:
        write_json(headers_path(payload.upload_id), [h.model_dump() for h in headers])
    except Exception as e:
        log.exception("Failed to write headers JSON | corr_id=%s", corr_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "WRITE_FAILED",
                "message": f"{type(e).__name__}: {e}",
                "corr_id": corr_id,
            },
        ) from e

    # Include corr_id so the frontend can correlate with logs
    # (Not in response_model; FastAPI will ignore extra keys unless you return a dict. So just return headers)
    return headers
