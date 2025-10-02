from __future__ import annotations

import importlib.util

import pytest

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("mineru") is None
    and importlib.util.find_spec("magic_pdf") is None,
    reason="MinerU client not installed",
)


def test_native_vs_mineru_parity_placeholder():
    """Placeholder test to ensure suite discovery when MinerU is available."""

    assert True
