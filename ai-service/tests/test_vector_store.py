import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings.embedder import embed_texts
from app.models import Chunk, Document
from app.retrieval.vector_store import similarity_search


async def _seed_document(
    session: AsyncSession, texts: list[str], collection_id: uuid.UUID, status: str = "DONE"
) -> uuid.UUID:
    document_id = uuid.uuid4()
    document = Document(
        id=document_id,
        collection_id=collection_id,
        filename="manual.pdf",
        content_hash=str(uuid.uuid4()),
        status=status,
        chunk_count=len(texts),
    )
    session.add(document)
    embeddings = embed_texts(texts)
    for index, (text, embedding) in enumerate(zip(texts, embeddings, strict=True)):
        session.add(
            Chunk(document_id=document_id, chunk_index=index, page_number=index + 1, content=text, embedding=embedding)
        )
    await session.commit()
    return document_id


async def test_similarity_search_ranks_the_relevant_chunk_first(db_session: AsyncSession) -> None:
    collection_id = uuid.uuid4()
    await _seed_document(
        db_session,
        [
            "The maximum torque for the M6 bolt is 12 Nm.",
            "Chocolate chip cookies need sea salt and softened butter.",
        ],
        collection_id,
    )

    query_embedding = embed_texts(["what is the maximum torque for the M6 bolt"])[0]
    results = await similarity_search(db_session, query_embedding, top_k=2)

    assert results[0].content.startswith("The maximum torque")


async def test_similarity_search_filters_by_collection(db_session: AsyncSession) -> None:
    collection_a = uuid.uuid4()
    collection_b = uuid.uuid4()
    await _seed_document(db_session, ["Fact only in collection A."], collection_a)
    await _seed_document(db_session, ["Fact only in collection B."], collection_b)

    query_embedding = embed_texts(["fact"])[0]
    results = await similarity_search(db_session, query_embedding, top_k=10, collection_id=collection_a)

    assert all("collection A" in r.content for r in results)


async def test_similarity_search_excludes_documents_not_marked_done(db_session: AsyncSession) -> None:
    collection_id = uuid.uuid4()
    await _seed_document(db_session, ["Still being processed."], collection_id, status="PROCESSING")

    query_embedding = embed_texts(["processed"])[0]
    results = await similarity_search(db_session, query_embedding, top_k=10, collection_id=collection_id)

    assert results == []
