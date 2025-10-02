"""PDF parser abstractions for SimpleSpecs (Phase P0 stubs)."""
from __future__ import annotations

from typing import List, Protocol

from ..config import Settings, get_settings
from ..models import ParsedObject


class PdfParser(Protocol):
    """Protocol describing PDF parsing behavior."""

    def parse(self, file_id: str, data: bytes | None = None) -> List[ParsedObject]:
        """Parse the provided PDF data into parsed objects."""


class MockPdfParser:
    """Stub parser that returns an empty result set."""

    def parse(self, file_id: str, data: bytes | None = None) -> List[ParsedObject]:
        return []


def get_pdf_parser(settings: Settings | None = None) -> PdfParser:
    """Return a parser implementation based on configuration."""

    settings = settings or get_settings()
    _ = settings.PDF_ENGINE  # Currently unused but validates access.
    return MockPdfParser()
