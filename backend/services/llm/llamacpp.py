"""llama.cpp chat completion provider."""
from __future__ import annotations

from typing import Any, List

import httpx

from .llm_provider import LLMProvider


class LlamaCPPProvider(LLMProvider):
    def __init__(self, *, model: str, params: dict[str, Any] | None, base_url: str) -> None:
        super().__init__(model=model, params=params)
        self.base_url = base_url.rstrip("/")

    async def _chat(self, messages: List[dict[str, str]]) -> str:
        payload: dict[str, Any] = {"model": self.model, "messages": messages}
        payload.update(self.params)
        url = f"{self.base_url}/v1/chat/completions"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:  # noqa: PERF203 - explicit handling
            raise RuntimeError(f"Unexpected response structure: {data}") from exc
