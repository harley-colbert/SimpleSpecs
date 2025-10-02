"""PDF parser abstractions for SimpleSpecs (Phase P0 stubs)."""
from __future__ import annotations

from typing import List, Protocol

from ..config import Settings, get_settings
from ..models import ParsedObject

__all__ = ["PdfParser", "select_pdf_parser"]


class PdfParser(Protocol):
    """Protocol describing PDF parsing behavior."""

    def parse(self, file_id: str, data: bytes | None = None) -> List[ParsedObject]:
        """Parse the provided PDF data into parsed objects."""


class MockPdfParser:
    """Stub parser that returns an empty result set."""

    def parse(self, file_id: str, data: bytes | None = None) -> List[ParsedObject]:
        return []


def select_pdf_parser(settings: Settings | None = None, file_path: str | None = None) -> PdfParser | None:
    """Return the placeholder parser for Phase P0."""

    settings = settings or get_settings()
    _ = settings.PDF_ENGINE  # Access to assert configuration availability.
    return MockPdfParser()


def get_pdf_parser(settings: Settings | None = None) -> PdfParser:
    """Backward-compatible accessor for the default parser."""

    parser = select_pdf_parser(settings=settings)
    assert parser is not None  # Narrow type for callers expecting a parser.
    return parser
