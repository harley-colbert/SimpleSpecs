"""PDF parser abstractions and selection logic for Phase 0."""
from __future__ import annotations

from typing import Optional, Protocol

from backend.config import Settings
from backend.models import ParsedObject


class PdfParser(Protocol):
    """Protocol describing a PDF parser implementation."""

    def parse_pdf(self, file_path: str) -> list[ParsedObject]:
        """Parse a PDF file and return parsed objects."""


class NativePdfParser:
    """Mock native PDF parser implementation."""

    def parse_pdf(self, file_path: str) -> list[ParsedObject]:  # pragma: no cover - placeholder behaviour
        return []


class MinerUPdfParser:
    """Mock MinerU PDF parser implementation."""

    def parse_pdf(self, file_path: str) -> list[ParsedObject]:  # pragma: no cover - placeholder behaviour
        return []


def select_pdf_parser(settings: Settings, file_path: str) -> Optional[PdfParser]:
    """Select a PDF parser based on the configured engine.

    Phase 0 does not yet provide real parser wiring, so this function returns
    ``None`` as a placeholder regardless of configuration. Later phases will
    supply the actual adapter selection.
    """

    _ = (settings, file_path)
    return None
