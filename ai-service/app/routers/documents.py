import time
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.ingestion.pipeline import ingest_document
from app.metrics import INGESTION_LATENCY, INGESTION_REQUESTS
from app.models import Document
from app.schemas import DocumentStatus, IngestResponse

router = APIRouter(prefix="/internal/documents", tags=["internal"])


def _to_status(document: Document) -> DocumentStatus:
    return DocumentStatus(
        document_id=document.id,
        status=document.status,
        chunk_count=document.chunk_count,
        content_hash=document.content_hash,
        error_message=document.error_message,
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    file: UploadFile = File(...),
    document_id: uuid.UUID = Form(...),
    collection_id: uuid.UUID = Form(...),
    session: AsyncSession = Depends(get_session),
) -> IngestResponse:
    """Called by the worker after it picks up a file from the upload watcher. Idempotent:
    re-ingesting the same bytes (even under a different document_id, e.g. a retried job) is
    detected via content hash and returns the existing record instead of re-embedding.
    """
    data = await file.read()
    start = time.perf_counter()
    result = await ingest_document(session, document_id, collection_id, file.filename or "unknown", data)
    INGESTION_LATENCY.observe(time.perf_counter() - start)
    INGESTION_REQUESTS.labels(status=result.status).inc()
    return result


@router.get("/by-hash/{content_hash}", response_model=DocumentStatus | None)
async def find_by_hash(content_hash: str, session: AsyncSession = Depends(get_session)) -> DocumentStatus | None:
    document = await session.scalar(select(Document).where(Document.content_hash == content_hash))
    return _to_status(document) if document is not None else None


@router.get("/{document_id}", response_model=DocumentStatus)
async def get_status(document_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> DocumentStatus:
    document = await session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return _to_status(document)


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> None:
    document = await session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    await session.delete(document)
    await session.commit()
