from pathlib import Path
from typing import Any

from worker.ai_client import AiServiceClient
from worker.gateway_client import GatewayClient
from worker.hashing import content_hash
from worker.logging import get_logger

logger = get_logger(__name__)


def ingest_document_job(
    document_id: str,
    collection_id: str,
    file_path: str,
    filename: str,
    correlation_id: str,
    sidecar_path: str | None = None,
    ai_client: AiServiceClient | None = None,
    gateway_client: GatewayClient | None = None,
) -> dict[str, Any]:
    """RQ job body, executed by an `rq worker` process (possibly on a retry after a transient
    failure - see the watcher's `Retry(...)` config).

    1. Idempotency pre-check: ask ai-service whether this exact content is already indexed, by
       hash, before uploading anything. This is a fast-path optimization only - even without it,
       ai-service's own unique constraint on content_hash makes step 2 idempotent on its own.
    2. Delegate the actual chunk/embed/store work to ai-service, which owns the RAG pipeline.
    3. Report the outcome to the gateway, whose JPA-owned `documents` row is what the frontend
       polls for upload status - this is the one place status becomes visible to the end user.
    4. Best-effort cleanup of the shared upload files; failure to clean up never fails the job,
       since the document is already durably indexed (or durably marked FAILED) by this point.
    """
    resolved_ai_client = ai_client or AiServiceClient()
    resolved_gateway_client = gateway_client or GatewayClient()

    path = Path(file_path)
    file_hash = content_hash(path)

    existing = resolved_ai_client.find_by_hash(file_hash, correlation_id)
    if existing is not None and existing.get("status") == "DONE":
        logger.info("job.duplicate_skip", document_id=document_id, existing_id=existing["document_id"])
        resolved_gateway_client.update_status(
            document_id, "DONE", existing["chunk_count"], None, correlation_id
        )
        _cleanup(path, sidecar_path)
        return existing

    logger.info("job.ingesting", document_id=document_id, filename=filename)
    data = path.read_bytes()
    result = resolved_ai_client.ingest(document_id, collection_id, filename, data, correlation_id)
    resolved_gateway_client.update_status(
        document_id, result["status"], result["chunk_count"], result.get("error_message"), correlation_id
    )
    logger.info("job.done", document_id=document_id, status=result["status"])
    _cleanup(path, sidecar_path)
    return result


def _cleanup(binary_path: Path, sidecar_path: str | None) -> None:
    for target in (binary_path, Path(sidecar_path) if sidecar_path else None):
        if target is None:
            continue
        try:
            target.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning("job.cleanup_failed", path=str(target), error=str(exc))
