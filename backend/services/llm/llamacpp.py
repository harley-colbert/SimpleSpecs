"""llama.cpp chat completion provider."""
from __future__ import annotations

from typing import Any, List
from urllib.parse import urlparse

import httpx

from .llm_provider import LLMProvider


class LlamaCPPProvider(LLMProvider):
    def __init__(self, *, model: str, params: dict[str, Any] | None, base_url: str) -> None:
        super().__init__(model=model, params=params)
        self.base_url = base_url.rstrip("/")

        params_copy = dict(self.params)
        endpoint_path = params_copy.pop("endpoint_path", None)
        self.params = params_copy

        if isinstance(endpoint_path, str) and endpoint_path.startswith("http"):
            self.request_url = endpoint_path.rstrip("/")
        elif isinstance(endpoint_path, str) and endpoint_path:
            self.request_url = f"{self.base_url}/{endpoint_path.lstrip('/')}"
        else:
            parsed = urlparse(self.base_url)
            if parsed.path and parsed.path != "/":
                self.request_url = self.base_url
            else:
                self.request_url = f"{self.base_url}/v1/chat/completions"

    async def _chat(self, messages: List[dict[str, str]]) -> str:
        payload: dict[str, Any] = {"model": self.model, "messages": messages}
        payload.update(self.params)
        payload.setdefault("stream", False)
        url = self.request_url
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        content: Any | None = None
        if isinstance(data, dict):
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                first_choice = choices[0]
                if isinstance(first_choice, dict):
                    message = first_choice.get("message")
                    if isinstance(message, dict):
                        content = message.get("content")
            if content is None:
                message = data.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
        if not isinstance(content, str):
            raise RuntimeError(f"Unexpected response structure: {data}")
        return content.strip()
