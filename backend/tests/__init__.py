"""Limit pytest collection to the new parser tests."""
from __future__ import annotations

from pathlib import Path

_TEST_DIR = Path(__file__).parent
collect_ignore = [
    path.name
    for path in _TEST_DIR.iterdir()
    if path.name.startswith("test_") and path.name != "test_parsers.py"
]
