"""SQLModel database models for persisting documents and processing steps."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel


class Document(SQLModel, table=True):
    """Represents a parsed document and its cached data."""

    __tablename__ = "documents"

    id: Optional[int] = Field(default=None, primary_key=True)
    upload_id: str = Field(index=True, unique=True, nullable=False)
    filename: str = Field(nullable=False)
    file_hash: str = Field(index=True, unique=True, nullable=False)
    object_count: int = Field(default=0, nullable=False)
    parsed_objects: list[Dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    steps: list["DocumentStep"] = Relationship(back_populates="document")


class DocumentStep(SQLModel, table=True):
    """Stores the state of a processing step (headers/specs/etc.) for a document."""

    __tablename__ = "document_steps"
    __table_args__ = (UniqueConstraint("document_id", "name", name="uq_document_step"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", nullable=False)
    name: str = Field(index=True, nullable=False)
    status: str = Field(default="pending", nullable=False)
    result: Optional[list[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON),
    )
    provider: Optional[str] = Field(default=None)
    model: Optional[str] = Field(default=None)
    params: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    base_url: Optional[str] = Field(default=None)
    api_key_used: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    document: Document = Relationship(back_populates="steps")
