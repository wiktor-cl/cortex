import httpx
import respx

from worker.ai_client import AiServiceClient


@respx.mock
def test_find_by_hash_returns_json_body() -> None:
    respx.get("http://ai-service.test/internal/documents/by-hash/abc123").mock(
        return_value=httpx.Response(
            200,
            json={
                "document_id": "d1",
                "status": "DONE",
                "chunk_count": 2,
                "content_hash": "abc123",
                "error_message": None,
            },
        )
    )
    client = AiServiceClient(base_url="http://ai-service.test")

    result = client.find_by_hash("abc123", correlation_id="corr-1")

    assert result is not None
    assert result["document_id"] == "d1"


@respx.mock
def test_find_by_hash_returns_none_for_unknown_hash() -> None:
    respx.get("http://ai-service.test/internal/documents/by-hash/unknown").mock(
        return_value=httpx.Response(200, content=b"null", headers={"content-type": "application/json"})
    )
    client = AiServiceClient(base_url="http://ai-service.test")

    assert client.find_by_hash("unknown", correlation_id="corr-1") is None


@respx.mock
def test_ingest_posts_multipart_with_correlation_header() -> None:
    route = respx.post("http://ai-service.test/internal/documents/ingest").mock(
        return_value=httpx.Response(
            200,
            json={"document_id": "d2", "status": "DONE", "chunk_count": 1, "content_hash": "x", "duplicate_of": None},
        )
    )
    client = AiServiceClient(base_url="http://ai-service.test")

    result = client.ingest("d2", "c1", "manual.txt", b"content", correlation_id="corr-1")

    assert result["status"] == "DONE"
    assert route.calls.last.request.headers["X-Correlation-Id"] == "corr-1"
