"""System capability routes for SimpleSpecs."""
from __future__ import annotations

import importlib
import shutil

from fastapi import APIRouter

from ..config import get_settings

system_router = APIRouter(prefix="/system", tags=["system"])


@system_router.get("/capabilities")
def get_capabilities() -> dict[str, bool | str]:
    """Return mock detection information for optional tooling."""

    settings = get_settings()
    capabilities = {
        "tesseract": shutil.which("tesseract") is not None,
        "ghostscript": shutil.which("gs") is not None,
        "java": shutil.which("java") is not None,
        "mineru_importable": False,
        "pdf_engine": settings.PDF_ENGINE,
    }
    try:
        importlib.import_module("mineru")
    except ModuleNotFoundError:
        capabilities["mineru_importable"] = False
    else:
        capabilities["mineru_importable"] = True
    return capabilities
