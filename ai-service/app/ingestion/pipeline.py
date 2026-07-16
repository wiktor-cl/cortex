import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.embeddings.embedder import embed_texts
from app.ingestion.chunker import chunk_pages
from app.ingestion.hashing import content_hash
from app.ingestion.loaders import load_document
from app.logging import get_logger
from app.models import Chunk, Document
from app.schemas import IngestResponse

logger = get_logger(__name__)


async def ingest_document(
    session: AsyncSession,
    document_id: uuid.UUID,
    collection_id: uuid.UUID,
    filename: str,
    data: bytes,
) -> IngestResponse:
    """Loads, chunks, embeds and stores a document - or short-circuits if it's already indexed.

    Idempotency is enforced by a unique constraint on `content_hash`: if the exact same bytes were
    already ingested (possibly under a different document_id, e.g. a retried worker job), this
    returns the existing record instead of embedding the content a second time. The document row is
    written in a single all-or-nothing commit alongside its chunks - a partially embedded document
    never becomes visible to retrieval. On failure, a FAILED row is written in its own clean
    transaction after rolling back the failed attempt, so status is always queryable via the API
    (never stuck at "we don't know").
    """
    hash_value = content_hash(data)

    existing = await session.scalar(select(Document).where(Document.content_hash == hash_value))
    if existing is not None:
        logger.info("ingest.duplicate", document_id=str(document_id), existing_id=str(existing.id))
        return IngestResponse(
            document_id=existing.id,
            status=existing.status,
            chunk_count=existing.chunk_count,
            content_hash=hash_value,
            duplicate_of=existing.id,
        )

    settings = get_settings()
    try:
        pages = load_document(filename, data)
        text_chunks = chunk_pages(pages, settings.chunk_size_chars, settings.chunk_overlap_chars)
        if not text_chunks:
            raise ValueError("Document produced no extractable text")

        embeddings = embed_texts([chunk.text for chunk in text_chunks])

        document = Document(
            id=document_id,
            collection_id=collection_id,
            filename=filename,
            content_hash=hash_value,
            status="DONE",
            chunk_count=len(text_chunks),
        )
        session.add(document)
        for text_chunk, embedding in zip(text_chunks, embeddings, strict=True):
            session.add(
                Chunk(
                    document_id=document_id,
                    chunk_index=text_chunk.chunk_index,
                    page_number=text_chunk.page_number,
                    content=text_chunk.text,
                    embedding=embedding,
                )
            )
        await session.commit()
        logger.info("ingest.done", document_id=str(document_id), chunk_count=len(text_chunks))
        return IngestResponse(
            document_id=document_id,
            status="DONE",
            chunk_count=len(text_chunks),
            content_hash=hash_value,
            duplicate_of=None,
        )
    except Exception as exc:
        await session.rollback()
        logger.error("ingest.failed", document_id=str(document_id), error=str(exc))
        failed_document = Document(
            id=document_id,
            collection_id=collection_id,
            filename=filename,
            content_hash=hash_value,
            status="FAILED",
            chunk_count=0,
            error_message=str(exc)[:1000],
        )
        session.add(failed_document)
        await session.commit()
        return IngestResponse(
            document_id=document_id,
            status="FAILED",
            chunk_count=0,
            content_hash=hash_value,
            duplicate_of=None,
        )
