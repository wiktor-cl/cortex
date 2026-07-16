from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from worker.config import get_settings

_RETRY = retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True)


class AiServiceClient:
    """Thin sync HTTP client for the two ai-service endpoints the worker needs. Retries are for
    transient network failures (ai-service warming up, brief connection blips) - a real ingestion
    failure (bad file, unsupported type) comes back as a 200 with status="FAILED", not an exception,
    so it is never masked by this retry.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = base_url or get_settings().ai_service_url

    @_RETRY
    def find_by_hash(self, content_hash: str, correlation_id: str) -> dict[str, Any] | None:
        with httpx.Client(base_url=self._base_url, timeout=30.0) as client:
            response = client.get(
                f"/internal/documents/by-hash/{content_hash}",
                headers={"X-Correlation-Id": correlation_id},
            )
            response.raise_for_status()
            body: dict[str, Any] | None = response.json()
            return body

    @_RETRY
    def ingest(
        self, document_id: str, collection_id: str, filename: str, data: bytes, correlation_id: str
    ) -> dict[str, Any]:
        with httpx.Client(base_url=self._base_url, timeout=120.0) as client:
            response = client.post(
                "/internal/documents/ingest",
                data={"document_id": document_id, "collection_id": collection_id},
                files={"file": (filename, data)},
                headers={"X-Correlation-Id": correlation_id},
            )
            response.raise_for_status()
            body: dict[str, Any] = response.json()
            return body
