from __future__ import annotations

import importlib.util

import pytest

from backend.config import get_settings
from backend.services.pdf_mineru import MinerUPdfParser, MinerUUnavailableError


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("mineru") is None
    and importlib.util.find_spec("magic_pdf") is None,
    reason="MinerU client not installed",
)


def test_mineru_parser_requires_enabled(monkeypatch):
    monkeypatch.setenv("SIMPLS_MINERU_ENABLED", "true")
    get_settings.cache_clear()
    settings = get_settings()
    with pytest.raises(MinerUUnavailableError):
        MinerUPdfParser(settings)
