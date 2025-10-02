"""LLM adapter protocol definitions for Phase 0."""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMAdapter(Protocol):
    """Protocol describing the interface for language model adapters."""

    def complete(self, prompt: str, *, temperature: float = 0.0, max_tokens: int | None = None) -> str:
        """Produce a completion for the provided prompt."""


class OpenRouterAdapter:
    """Placeholder adapter for the OpenRouter API."""

    def complete(self, prompt: str, *, temperature: float = 0.0, max_tokens: int | None = None) -> str:  # pragma: no cover
        raise NotImplementedError("OpenRouter integration is implemented in a later phase")


class LlamaCppAdapter:
    """Placeholder adapter for a local llama.cpp server."""

    def complete(self, prompt: str, *, temperature: float = 0.0, max_tokens: int | None = None) -> str:  # pragma: no cover
        raise NotImplementedError("llama.cpp integration is implemented in a later phase")
