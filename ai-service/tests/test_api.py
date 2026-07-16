import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.main import app


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    # follow_redirects=True: the mounted /metrics sub-app 307-redirects "/metrics" -> "/metrics/"
    # (standard Starlette mount behavior), which real scrapers and browsers follow transparently.
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as async_client:
        yield async_client
    app.dependency_overrides.clear()


async def test_health_endpoint_reports_healthy(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


async def test_metrics_endpoint_exposes_prometheus_format(client: AsyncClient) -> None:
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert b"# HELP" in response.content
    # A default prometheus_client metric that doesn't depend on /proc (unavailable on Windows),
    # unlike the process_* collector metrics - keeps this test OS-independent.
    assert b"python_gc_objects_collected_total" in response.content


async def test_metrics_endpoint_reflects_query_requests(client: AsyncClient) -> None:
    await client.post("/query", json={"question": "Anything at all"})

    response = await client.get("/metrics")

    assert b"cortex_ai_query_requests_total" in response.content


async def test_ingest_then_query_returns_extractive_answer_with_citation(client: AsyncClient) -> None:
    document_id = uuid.uuid4()
    collection_id = uuid.uuid4()
    content = b"The maximum operating pressure of tank B is 8 bar. Never exceed 8 bar during testing."

    ingest_response = await client.post(
        "/internal/documents/ingest",
        files={"file": ("pressure-manual.txt", content, "text/plain")},
        data={"document_id": str(document_id), "collection_id": str(collection_id)},
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["status"] == "DONE"

    query_response = await client.post(
        "/query",
        json={"question": "What is the maximum operating pressure of tank B?", "collection_id": str(collection_id)},
    )

    assert query_response.status_code == 200
    body = query_response.json()
    assert body["mode"] == "extractive"
    assert len(body["citations"]) >= 1
    assert body["citations"][0]["filename"] == "pressure-manual.txt"
    assert "8 bar" in body["answer"]


async def test_ingest_same_content_twice_is_idempotent(client: AsyncClient) -> None:
    content = b"Duplicate content for the idempotency check across two uploads."

    first = await client.post(
        "/internal/documents/ingest",
        files={"file": ("a.txt", content, "text/plain")},
        data={"document_id": str(uuid.uuid4()), "collection_id": str(uuid.uuid4())},
    )
    second = await client.post(
        "/internal/documents/ingest",
        files={"file": ("b.txt", content, "text/plain")},
        data={"document_id": str(uuid.uuid4()), "collection_id": str(uuid.uuid4())},
    )

    assert first.json()["document_id"] == second.json()["document_id"]
    assert second.json()["duplicate_of"] == first.json()["document_id"]


async def test_query_with_no_matching_documents_returns_not_found_message(client: AsyncClient) -> None:
    response = await client.post("/query", json={"question": "Anything at all", "collection_id": str(uuid.uuid4())})

    assert response.status_code == 200
    assert "Nie znalazłem" in response.json()["answer"]


async def test_get_document_status_after_ingest(client: AsyncClient) -> None:
    document_id = uuid.uuid4()
    await client.post(
        "/internal/documents/ingest",
        files={"file": ("status-check.txt", b"Status check content here.", "text/plain")},
        data={"document_id": str(document_id), "collection_id": str(uuid.uuid4())},
    )

    response = await client.get(f"/internal/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "DONE"


async def test_get_document_status_unknown_id_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/internal/documents/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_query_validation_rejects_empty_question(client: AsyncClient) -> None:
    response = await client.post("/query", json={"question": ""})

    assert response.status_code == 422
