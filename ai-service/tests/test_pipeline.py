import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.pipeline import ingest_document


async def test_ingest_document_chunks_embeds_and_marks_done(db_session: AsyncSession) -> None:
    document_id = uuid.uuid4()
    data = b"The system requires 24V DC power. Always disconnect power before servicing the unit."

    result = await ingest_document(db_session, document_id, uuid.uuid4(), "notes.txt", data)

    assert result.status == "DONE"
    assert result.chunk_count >= 1
    assert result.document_id == document_id
    assert result.duplicate_of is None


async def test_ingest_document_is_idempotent_on_identical_content(db_session: AsyncSession) -> None:
    data = b"Identical bytes ingested twice should not be indexed twice."

    first = await ingest_document(db_session, uuid.uuid4(), uuid.uuid4(), "a.txt", data)
    second = await ingest_document(db_session, uuid.uuid4(), uuid.uuid4(), "b.txt", data)

    assert second.document_id == first.document_id
    assert second.duplicate_of == first.document_id
    assert second.chunk_count == first.chunk_count


async def test_ingest_document_marks_failed_for_unsupported_extension(db_session: AsyncSession) -> None:
    result = await ingest_document(db_session, uuid.uuid4(), uuid.uuid4(), "firmware.exe", b"binary data")

    assert result.status == "FAILED"
    assert result.chunk_count == 0


async def test_ingest_document_marks_failed_when_no_extractable_text(db_session: AsyncSession) -> None:
    result = await ingest_document(db_session, uuid.uuid4(), uuid.uuid4(), "empty.txt", b"   ")

    assert result.status == "FAILED"
