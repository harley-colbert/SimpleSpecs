"""Pydantic schemas defining the public API contracts."""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ParsedObject(BaseModel):
    """One extracted text/table/image object."""

    object_id: str = Field(..., description="Stable identifier for the parsed object.")
    file_id: str = Field(..., description="Identifier of the parent file.")
    kind: Literal["text", "table", "image"] = Field(..., description="Type of content represented by the object.")
    text: Optional[str] = Field(default=None, description="Extracted text, when available.")
    page_index: Optional[int] = Field(default=None, description="Zero-based page index containing the object.")
    bbox: Optional[list[float]] = Field(default=None, description="Bounding box [x0, y0, x1, y1] in PDF coordinates.")
    order_index: int = Field(..., description="Linear order of the object within the document.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional parser-specific metadata.")


class SectionSpan(BaseModel):
    """Span of parsed objects covered by a section."""

    start_object: Optional[str] = Field(default=None, description="First parsed object id in the section span.")
    end_object: Optional[str] = Field(default=None, description="Last parsed object id in the section span.")


class SectionNode(BaseModel):
    """Hierarchical section tree node."""

    section_id: str = Field(..., description="Unique identifier for the section node.")
    file_id: str = Field(..., description="Identifier of the file this section belongs to.")
    number: Optional[str] = Field(default=None, description="Section numbering label if present.")
    title: str = Field(..., description="Section title text.")
    depth: int = Field(..., ge=0, description="Depth of the node in the hierarchy (root=0).")
    children: list["SectionNode"] = Field(default_factory=list, description="Child section nodes.")
    span: SectionSpan = Field(default_factory=SectionSpan, description="Span of parsed objects covered by the section.")


class SpecItem(BaseModel):
    """Structured specification item extracted from a section."""

    spec_id: str = Field(..., description="Unique identifier for the specification item.")
    file_id: str = Field(..., description="Identifier of the file the spec belongs to.")
    section_id: str = Field(..., description="Section identifier the spec originated from.")
    section_number: Optional[str] = Field(default=None, description="Numbering label of the parent section.")
    section_title: str = Field(..., description="Title of the parent section.")
    spec_text: str = Field(..., description="Extracted specification text content.")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence score supplied by the extractor.")
    source_object_ids: list[str] = Field(default_factory=list, description="Identifiers of parsed objects supporting the spec.")


class MockFileSummary(BaseModel):
    """Summary payload used by mock routes for convenience."""

    file_id: str
    parsed_objects: list[ParsedObject]
    sections: list[SectionNode]
    specs: list[SpecItem]
    pdf_engine: Literal["native", "mineru", "auto"]
