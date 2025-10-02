"""System routes."""
from __future__ import annotations

import importlib
import shutil

from fastapi import APIRouter


system_router = APIRouter(prefix="/system", tags=["system"])


@system_router.get("/capabilities", summary="Report availability of optional tools.")
def get_capabilities() -> dict[str, bool]:
    """Return capability flags for optional external tooling."""

    try:
        importlib.import_module("mineru")
        mineru_importable = True
    except ImportError:  # pragma: no cover - depends on environment
        mineru_importable = False

    return {
        "tesseract": shutil.which("tesseract") is not None,
        "ghostscript": shutil.which("gs") is not None,
        "java": shutil.which("java") is not None,
        "mineru_importable": mineru_importable,
    }
