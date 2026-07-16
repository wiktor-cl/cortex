import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from worker.config import get_settings

_RETRY = retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), reraise=True)


class GatewayClient:
    """Reports ingestion outcomes back to the gateway's internal status-callback endpoint, so its
    JPA-owned `documents` table (what the frontend actually reads) reflects the RAG engine's result
    without the gateway having to poll ai-service. Authenticated with a shared internal API key
    header rather than a user JWT - this is service-to-service, not a user-initiated call.
    """

    def __init__(self, base_url: str | None = None) -> None:
        settings = get_settings()
        self._base_url = base_url or settings.gateway_internal_url
        self._api_key = settings.internal_api_key

    @_RETRY
    def update_status(
        self,
        document_id: str,
        status: str,
        chunk_count: int,
        error_message: str | None,
        correlation_id: str,
    ) -> None:
        with httpx.Client(base_url=self._base_url, timeout=30.0) as client:
            response = client.patch(
                f"/internal/documents/{document_id}/status",
                # camelCase on the wire here, not snake_case: this call crosses into the Java
                # gateway's convention, unlike the ai_client calls which stay in Python's snake_case.
                json={"status": status, "chunkCount": chunk_count, "errorMessage": error_message},
                headers={"X-Internal-Api-Key": self._api_key, "X-Correlation-Id": correlation_id},
            )
            response.raise_for_status()
