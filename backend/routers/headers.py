"""Headers extraction endpoint with optional Ollama direct-call mode."""
from __future__ import annotations

import re
from typing import List, Dict, Any, Optional

import httpx
from fastapi import APIRouter, HTTPException, status

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


def _is_ollama_mode(provider_name: Optional[str], base_url: Optional[str]) -> bool:
    """
    Decide whether to use direct Ollama-style /api/chat call.

    True if:
      - provider == "ollama" (case-insensitive), OR
      - base_url endswith "/api/chat"
    """
    if provider_name and provider_name.lower() == "ollama":
        return True
    if base_url and base_url.rstrip("/").endswith("/api/chat"):
        return True
    return False


def _ollama_endpoint(base_url: str) -> str:
    """
    Build the Ollama /api/chat endpoint from a provided base_url.
    If the caller gave the full /api/chat URL already, keep it.
    Otherwise, append /api/chat.
    """
    base = base_url.rstrip("/")
    if base.endswith("/api/chat"):
        return base
    return f"{base}/api/chat"


async def _chat_via_ollama(
    *,
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    params: Optional[Dict[str, Any]],
    timeout: float = 60.0,
) -> str:
    """
    Direct Ollama call that mirrors the simple example in `ollama_test.py`.

    Payload shape (matching your example):
      {
        "model": MODEL,
        "messages": [...],
        "stream": false,
        ...params  # merged at the root (same as your example style)
      }

    Response shape (expected):
      {"message": {"content": "<text>"}, ...}
    """
    url = _ollama_endpoint(base_url)
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if params:
        # Match your example: merge params at root (not "options")
        payload.update(params)

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        resp = await client.post(url, json=payload)
        # Raise helpful error if Ollama returns non-2xx
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Ollama call failed ({resp.status_code}): {resp.text}",
            ) from e

        data = resp.json()

    # Primary expected path
    try:
        content = data["message"]["content"]
    except (KeyError, TypeError):
        # Graceful fallbacks if server returns a slightly different shape
        content = None
        if isinstance(data, dict):
            # Some builds may still return OpenAI-like "choices"
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                choice0 = choices[0]
                if isinstance(choice0, dict):
                    msg = choice0.get("message")
                    if isinstance(msg, dict):
                        content = msg.get("content")

    if not isinstance(content, str) or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama returned unexpected response shape: {data}",
        )
    return content.strip()


@router.post("/headers", response_model=list[HeaderItem])
async def extract_headers(payload: HeadersRequest) -> List[HeaderItem]:
    """
    Extract a numbered nested list of headers/subheaders from an uploaded document.

    If `payload.provider == "ollama"` (or base_url ends with `/api/chat`), the endpoint will
    call Ollama directly using the same payload style as `ollama_test.py`.
    Otherwise it will use the configured LLM provider via `get_provider(...).chat(messages)`.
    """
    # --- Load document objects/text ---
    objects_raw = read_jsonl(upload_objects_path(payload.upload_id))
    if not objects_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    document = document_text(objects_raw)
    if not document.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document is empty")

    # --- Build the messages array (works for both OpenAI/llama.cpp and Ollama) ---
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "You analyze engineering specification documents."},
        {
            "role": "user",
            "content": f"{_HEADERS_PROMPT}\n\nDocument contents:\n{document}",
        },
    ]

    # --- Choose call path: Ollama-direct vs Provider abstraction ---
    use_ollama = _is_ollama_mode(payload.provider, payload.base_url)

    if use_ollama:
        if not payload.base_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="base_url is required for Ollama mode",
            )
        if not payload.model:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="model is required for Ollama mode",
            )

        # Direct call to Ollama /api/chat with your example payload shape
        response_text = await _chat_via_ollama(
            base_url=payload.base_url,
            model=payload.model,
            messages=messages,
            params=payload.params,
        )
    else:
        # Use your existing provider abstraction for llama.cpp OpenAI-compatible, OpenRouter, etc.
        provider = get_provider(
            payload.provider,
            model=payload.model,
            params=payload.params,
            api_key=payload.api_key,
            base_url=payload.base_url,
        )
        response_text = await provider.chat(messages)

    # --- Parse fenced #headers# block ---
    match = re.search(r"#headers#(.*?)#headers#", response_text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM returned unexpected format (missing #headers# fence)",
        )

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
        # If the LLM responded but with no usable lines, 422 is also a fair choice.
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No headers parsed")

    write_json(headers_path(payload.upload_id), [header.model_dump() for header in headers])
    return headers
