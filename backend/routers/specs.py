"""Specification extraction routes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Query, status

from ..config import get_settings
from ..models import ParsedObject, SectionNode, SpecItem
from ..services.llm_client import LlamaCppAdapter, OpenRouterAdapter
from ..services.specs import extract_specs_for_sections

specs_router = APIRouter(prefix="/specs", tags=["specs"])


def _load_parsed_objects(file_id: str) -> list[ParsedObject]:
    settings = get_settings()
    target = Path(settings.ARTIFACTS_DIR) / file_id / "parsed" / "objects.json"
    if not target.exists():
        raise FileNotFoundError("parsed_missing")
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return [ParsedObject.model_validate(item) for item in data]


def _load_sections(file_id: str) -> SectionNode:
    settings = get_settings()
    target = Path(settings.ARTIFACTS_DIR) / file_id / "headers" / "sections.json"
    if not target.exists():
        raise FileNotFoundError("sections_missing")
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return SectionNode.model_validate(data)


def _load_persisted_specs(file_id: str) -> list[SpecItem]:
    settings = get_settings()
    target = Path(settings.ARTIFACTS_DIR) / file_id / "specs" / "specs.json"
    if not target.exists():
        raise FileNotFoundError("specs_missing")
    with target.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [SpecItem.model_validate(item) for item in payload]


def _select_adapter(name: str | None):
    if name is None or name.lower() == "openrouter":
        return OpenRouterAdapter()
    if name.lower() == "llamacpp":
        return LlamaCppAdapter()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported llm adapter.",
    )


@specs_router.post("/{file_id}/find", response_model=List[SpecItem])
def find_spec_items(file_id: str, llm: str | None = Query(default=None)) -> List[SpecItem]:
    """Run spec extraction for the requested file and persist results."""

    adapter = _select_adapter(llm)
    try:
        objects = _load_parsed_objects(file_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parsed objects not found.",
        ) from exc
    try:
        sections = _load_sections(file_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Header sections not found. Run phase 2.",
        ) from exc
    try:
        return extract_specs_for_sections(file_id, sections, objects, adapter)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Section chunks not found. Run phase 3.",
        ) from exc


@specs_router.get("/{file_id}", response_model=List[SpecItem])
def get_spec_items(file_id: str) -> List[SpecItem]:
    """Return persisted specification items for the file."""

    try:
        return _load_persisted_specs(file_id)
    except FileNotFoundError:
        pass

    try:
        objects = _load_parsed_objects(file_id)
        sections = _load_sections(file_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specs not found.",
        ) from exc

    try:
        extract_specs_for_sections(file_id, sections, objects, OpenRouterAdapter())
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specs not found.",
        ) from exc

    try:
        return _load_persisted_specs(file_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specs not found.",
        ) from exc
