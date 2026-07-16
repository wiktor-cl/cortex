import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chunk, Document


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    content: str
    page_number: int | None
    chunk_index: int
    score: float


async def similarity_search(
    session: AsyncSession,
    query_embedding: list[float],
    top_k: int,
    collection_id: uuid.UUID | None = None,
) -> list[RetrievedChunk]:
    """Top-k nearest chunks by cosine distance.

    Embeddings are stored L2-normalized, so cosine distance and Euclidean
    distance rank candidates identically here - cosine is used because it is
    the conventional similarity measure for sentence embeddings and pgvector
    can index it directly (`vector_cosine_ops`).
    """
    distance = Chunk.embedding.cosine_distance(query_embedding)
    statement = (
        select(Chunk, Document.filename, distance.label("distance"))
        .join(Document, Chunk.document_id == Document.id)
        .where(Document.status == "DONE")
    )
    if collection_id is not None:
        statement = statement.where(Document.collection_id == collection_id)
    statement = statement.order_by(distance).limit(top_k)

    result = await session.execute(statement)
    return [
        RetrievedChunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            filename=filename,
            content=chunk.content,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            score=1.0 - float(distance_value),
        )
        for chunk, filename, distance_value in result.all()
    ]
