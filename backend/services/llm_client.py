"""LLM client abstractions for SimpleSpecs (Phase P0 stubs)."""
from __future__ import annotations

from typing import Any, Protocol


class LLMClient(Protocol):
    """Protocol describing minimal LLM interaction."""

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response for the given prompt."""


class NullLLMClient:
    """Stub LLM client used during early phases."""

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        return "LLM functionality not implemented in Phase P0."


def get_llm_client() -> LLMClient:
    """Return the stub LLM client."""

    return NullLLMClient()
