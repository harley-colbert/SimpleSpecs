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
Return ONLY the list enclosed in #headers# fencing, #headers#


"""

# ---------------------------
# Ollama helpers
# ---------------------------

def _is_ollama_mode(provider_name: Optional[str], base_url: Optional[str]) -> bool:
    """Use direct Ollama if provider='ollama' or base_url already points to /api/chat or /api/generate."""
    if provider_name and provider_name.lower() == "ollama":
        return True
    if base_url:
        base = base_url.rstrip("/")
        if base.endswith("/api/chat") or base.endswith("/api/generate"):
            return True
    return False


def _ollama_chat_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    return base if base.endswith("/api/chat") else f"{base}/api/chat"


def _ollama_generate_url(base_url: str) -> str:
    base = base_url.rstrip("/")
    return base if base.endswith("/api/generate") else f"{base}/api/generate"


def _flatten_messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """Flatten chat messages into a single prompt suitable for /api/generate."""
    parts: List[str] = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        parts.append(f"{role.upper()}: {content}")
    parts.append("ASSISTANT:")
    return "\n\n".join(parts)


def _normalize_ollama_options(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Map OpenAI-like params to Ollama 'options' and pass-through known Ollama options.
    - max_tokens -> num_predict
    - temperature -> temperature
    """
    if not params:
        return {}
    options: Dict[str, Any] = {}

    # Common OpenAI → Ollama mappings
    if "max_tokens" in params:
        options["num_predict"] = params["max_tokens"]
    if "temperature" in params:
        options["temperature"] = params["temperature"]

    # Pass-through known Ollama options if provided
    passthrough_keys = (
        "num_predict", "top_k", "top_p", "presence_penalty", "frequency_penalty", "stop",
        "repeat_penalty", "repeat_last_n", "mirostat", "mirostat_tau", "mirostat_eta"
    )
    for k in passthrough_keys:
        if k in params:
            options[k] = params[k]

    return options


def _extract_content_tolerant(data: Any) -> Optional[str]:
    """Handle multiple valid Ollama response shapes."""
    # /api/chat canonical
    if isinstance(data, dict):
        msg = data.get("message")
        if isinstance(msg, dict):
            c = msg.get("content")
            if isinstance(c, str) and c.strip():
                return c

    # /api/generate canonical
    if isinstance(data, dict):
        c = data.get("response")
        if isinstance(c, str) and c.strip():
            return c

    # OpenAI-like
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                msg = first.get("message")
                if isinstance(msg, dict):
                    c = msg.get("content")
                    if isinstance(c, str) and c.strip():
                        return c

    # Older variants: messages list
    if isinstance(data, dict):
        msgs = data.get("messages")
        if isinstance(msgs, list) and msgs:
            last = msgs[-1]
            if isinstance(last, dict):
                c = last.get("content")
                if isinstance(c, str) and c.strip():
                    return c

    return None


def _strip_reasoning_tags(text: str) -> str:
    """
    Trim <think>...</think> blocks some reasoning models emit (e.g., deepseek-r1).
    Keeps only the final visible answer.
    """
    if not text or "<think>" not in text:
        return text
    # Remove all <think>...</think> segments
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


async def _chat_via_ollama(
    *,
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    params: Optional[Dict[str, Any]] = None,
    timeout: float = 60.0,
    combine_to_single_prompt: bool = True,
) -> str:
    """
    Direct Ollama call mirroring the simple requests example.
    - If combine_to_single_prompt=False: POST /api/chat with {"model","messages","stream":false}
    - If combine_to_single_prompt=True:  POST /api/generate with {"model","prompt","stream":false}
    Puts gen options under "options": {...} and parses multiple response shapes.
    """
    oheaders = {"Content-Type": "application/json", "Accept": "application/json"}

    if combine_to_single_prompt:
        url = _ollama_generate_url(base_url)
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": _flatten_messages_to_prompt(messages),
            "stream": False,
        }
    else:
        url = _ollama_chat_url(base_url)
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

    # Attach Ollama options
    options = _normalize_ollama_options(params)
    if options:
        payload["options"] = {**payload.get("options", {}), **options}

    # Allow extra root-level fields too (keeps parity with your test harness)
    if params:
        for k, v in params.items():
            if k not in ("max_tokens",) and k not in options:
                payload[k] = v

    async with httpx.AsyncClient(timeout=timeout, headers=oheaders) as client:
        try:
            # Debug log (small snippet) for payload visibility
            short_payload = {k: (v if k != "messages" else f"[{len(messages)} messages]") for k, v in payload.items()}
            print(f"[headers.py] POST {url} {payload}")
            resp = await client.post(url, json=payload)
            print(f"[headers.py] {resp}")
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Ollama call failed ({resp.status_code}): {resp.text}",
            ) from e
            print(f"[headers.py] {resp}")
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Ollama connection error: {e!r}",
            ) from e

        try:
            data = resp.json()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Ollama returned non-JSON: {resp.text[:1000]}",
            )

    content = _extract_content_tolerant(data)
    if not content or not isinstance(content, str) or not content.strip():
        snippet = str(data)
        if len(snippet) > 2000:
            snippet = snippet[:2000] + " ... [truncated]"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama returned unexpected response shape: {snippet}",
        )

    return _strip_reasoning_tags(content.strip())

# ---------------------------
# Endpoint
# ---------------------------

@router.post("/headers", response_model=list[HeaderItem])
async def extract_headers(payload: HeadersRequest) -> List[HeaderItem]:
    """
    Extract a numbered nested list of headers/subheaders from an uploaded document.

    If `payload.provider == "ollama"` (or base_url ends with `/api/chat` or `/api/generate`), the endpoint will
    call Ollama directly using a payload compatible with your `ollama_test.py` style.
    Otherwise it will use the configured LLM provider via `get_provider(...).chat(messages)`.
    """
    # Load document
    objects_raw = read_jsonl(upload_objects_path(payload.upload_id))
    if not objects_raw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    document = document_text(objects_raw)
    if not document.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document is empty")

    # Build chat
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "You analyze engineering specification documents."},
        {"role": "user", "content": f"{_HEADERS_PROMPT}\n\nDocument contents:\n{document}"},
    ]

    # Decide path
    use_ollama = _is_ollama_mode(payload.provider, payload.base_url)

    if use_ollama:
        print("[headers.py] Using Ollama mode")
        if not payload.base_url:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="base_url is required for Ollama mode")
        if not payload.model:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="model is required for Ollama mode")

        # If caller explicitly wants single-string prompt, allow via params flag
        combine = bool(getattr(payload, "combine_to_single_prompt", False) or (payload.params or {}).get("combine_to_single_prompt"))
        response_text = await _chat_via_ollama(
            base_url=payload.base_url,
            model=payload.model,
            messages=messages,
            params=payload.params,
            timeout=float((payload.params or {}).get("timeout", 60.0)),
            combine_to_single_prompt=combine,
        )
    else:
        provider = get_provider(
            payload.provider,
            model=payload.model,
            params=payload.params,
            api_key=payload.api_key,
            base_url=payload.base_url,
        )
        response_text = await provider.chat(messages)

    # Parse fenced #headers# block
    match = re.search(r"#headers#(.*?)#headers#", response_text, re.DOTALL | re.IGNORECASE)
    if not match:
        # Provide a useful preview to debug prompts
        preview = response_text[:800] + (" ... [truncated]" if len(response_text) > 800 else "")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM returned unexpected format (missing #headers# fence). Preview: {preview}",
        )

    content = match.group(1)
    headers: List[HeaderItem] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        mline = re.match(r"^(\d+(?:\.\d+)*)[\s\-\.]+(.+)$", line)
        if not mline:
            continue
        section_number = mline.group(1).strip()
        section_name = mline.group(2).strip()
        headers.append(HeaderItem(section_number=section_number, section_name=section_name))

    if not headers:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="No headers parsed from fenced block")

    write_json(headers_path(payload.upload_id), [h.model_dump() for h in headers])
    return headers
