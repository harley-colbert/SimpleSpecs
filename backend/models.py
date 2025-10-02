"""Pydantic models describing core API contracts for SimpleSpecs."""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Represents a rectangular bounding box on a page."""

    x0: float = Field(ge=0)
    y0: float = Field(ge=0)
    x1: float = Field(ge=0)
    y1: float = Field(ge=0)


class ParsedObject(BaseModel):
    """One extracted text/table/image object."""

    object_id: str
    file_id: str
    kind: Literal["text", "table", "image"]
    text: Optional[str] = None
    page_index: Optional[int] = Field(default=None, ge=0)
    bbox: Optional[BoundingBox] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SectionNode(BaseModel):
    """Section tree node produced during header discovery."""

    section_id: str
    title: str
    level: int = Field(ge=0)
    page_start: Optional[int] = Field(default=None, ge=0)
    page_end: Optional[int] = Field(default=None, ge=0)
    object_ids: List[str] = Field(default_factory=list)
    children: List["SectionNode"] = Field(default_factory=list)


class SpecItem(BaseModel):
    """Specification item extracted from a section."""

    spec_id: str
    section_id: str
    title: str
    content: str
    status: Literal["draft", "confirmed", "rejected"] = "draft"
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


SectionNode.model_rebuild()
