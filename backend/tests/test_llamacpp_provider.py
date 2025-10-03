"""Tests for the llama.cpp provider integration."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.services.llm.llamacpp import LlamaCPPProvider


def _make_mock_async_client(
    expected_url: str,
    expected_payload: dict,
    response_json: dict,
):
    class _MockAsyncClient:
        def __init__(self, *args, **kwargs) -> None:  # noqa: D401 - test helper
            pass

        async def __aenter__(self) -> "_MockAsyncClient":
            return self

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

        async def post(self, url: str, json: dict):
            assert url == expected_url
            assert json == expected_payload
            request = httpx.Request("POST", expected_url, json=json)
            return httpx.Response(200, json=response_json, request=request)

    return _MockAsyncClient


def test_llamacpp_provider_openai_style(monkeypatch):
    messages = [{"role": "user", "content": "Hi"}]
    provider = LlamaCPPProvider(
        model="test-model",
        params={"temperature": 0.7},
        base_url="http://llama.example",
    )
    expected_payload = {
        "model": "test-model",
        "messages": messages,
        "temperature": 0.7,
        "stream": False,
    }
    response_json = {"choices": [{"message": {"content": "Hello! "}}]}
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        _make_mock_async_client("http://llama.example/v1/chat/completions", expected_payload, response_json),
    )

    result = asyncio.run(provider._chat(messages))

    assert result == "Hello!"


def test_llamacpp_provider_ollama_style(monkeypatch):
    messages = [{"role": "user", "content": "Tell me a joke"}]
    provider = LlamaCPPProvider(
        model="ollama-model",
        params={"endpoint_path": "/api/chat", "stream": True},
        base_url="http://localhost:11434",
    )
    expected_payload = {
        "model": "ollama-model",
        "messages": messages,
        "stream": True,
    }
    response_json = {"message": {"role": "assistant", "content": "Knock knock."}}
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        _make_mock_async_client("http://localhost:11434/api/chat", expected_payload, response_json),
    )

    result = asyncio.run(provider._chat(messages))

    assert result == "Knock knock."
