"""Helpers for persisting and retrieving document processing data."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable, Sequence

from fastapi import HTTPException, status
from sqlmodel import select

from ..db import get_session
from ..db_models import Document, DocumentStep


def get_document_by_hash(file_hash: str) -> Document | None:
    with get_session() as session:
        statement = select(Document).where(Document.file_hash == file_hash)
        return session.exec(statement).first()


def get_document(upload_id: str) -> Document | None:
    with get_session() as session:
        statement = select(Document).where(Document.upload_id == upload_id)
        return session.exec(statement).first()


def get_document_or_404(upload_id: str) -> Document:
    document = get_document(upload_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    return document


def create_document(
    *,
    upload_id: str,
    filename: str,
    file_hash: str,
    parsed_objects: Sequence[dict[str, Any]],
) -> Document:
    document = Document(
        upload_id=upload_id,
        filename=filename,
        file_hash=file_hash,
        object_count=len(parsed_objects),
        parsed_objects=list(parsed_objects),
    )
    with get_session() as session:
        session.add(document)
        session.commit()
        session.refresh(document)
    return document


def clone_document(existing: Document, *, upload_id: str) -> Document:
    document = Document(
        upload_id=upload_id,
        filename=existing.filename,
        file_hash=existing.file_hash,
        object_count=existing.object_count,
        parsed_objects=list(existing.parsed_objects or []),
    )
    with get_session() as session:
        session.add(document)
        session.commit()
        session.refresh(document)

        for step in existing.steps:
            new_step = DocumentStep(
                document_id=document.id,
                name=step.name,
                status=step.status,
                result=list(step.result or []),
                provider=step.provider,
                model=step.model,
                params=step.params,
                base_url=step.base_url,
                api_key_used=step.api_key_used,
            )
            session.add(new_step)
        session.commit()
        session.refresh(document)
    return document


def upsert_step(
    upload_id: str,
    *,
    name: str,
    result: Iterable[dict[str, Any]] | None,
    provider: str | None,
    model: str | None,
    params: dict[str, Any] | None,
    base_url: str | None,
    api_key_used: bool,
    status_value: str = "completed",
) -> None:
    with get_session() as session:
        statement = select(Document).where(Document.upload_id == upload_id)
        document = session.exec(statement).first()
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

        step_stmt = select(DocumentStep).where(
            (DocumentStep.document_id == document.id) & (DocumentStep.name == name)
        )
        step = session.exec(step_stmt).first()
        if not step:
            step = DocumentStep(
                document_id=document.id,
                name=name,
            )
            session.add(step)

        step.status = status_value
        step.result = list(result) if result is not None else None
        step.provider = provider
        step.model = model
        step.params = params
        step.base_url = base_url
        step.api_key_used = api_key_used
        step.updated_at = datetime.utcnow()

        session.add(step)
        session.commit()


def get_step(upload_id: str, name: str) -> DocumentStep | None:
    with get_session() as session:
        statement = (
            select(DocumentStep)
            .join(Document, DocumentStep.document_id == Document.id)
            .where((Document.upload_id == upload_id) & (DocumentStep.name == name))
        )
        return session.exec(statement).first()
