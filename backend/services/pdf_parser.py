"""PDF parser abstractions and selection logic."""
from __future__ import annotations

from typing import Protocol

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


def select_pdf_parser(settings: Settings, file_path: str) -> PdfParser:
    """Select a PDF parser based on the configured engine."""

    engine = settings.PDF_ENGINE
    if engine == "native":
        return NativePdfParser()
    if engine == "mineru":
        return MinerUPdfParser()
    if engine == "auto":
        return MinerUPdfParser() if settings.MINERU_ENABLED else NativePdfParser()

    raise ValueError(f"Unsupported PDF engine: {engine}")
