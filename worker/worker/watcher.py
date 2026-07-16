import json
from pathlib import Path
from typing import Any

from rq import Retry
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver

from worker.config import get_settings
from worker.jobs import ingest_document_job
from worker.logging import get_logger
from worker.queue import get_queue

logger = get_logger(__name__)


class UploadSidecarHandler(FileSystemEventHandler):
    """Watches for `{document_id}.json` sidecar files written by the gateway.

    The gateway writes the document's bytes first, then the JSON sidecar last - so the sidecar's
    appearance is the signal that the upload is complete and safe to enqueue. Watching the sidecar
    (instead of the binary) avoids racing a partially-written file, which watchdog would otherwise
    report as "created" the instant the OS opens it for writing.
    """

    def __init__(self, uploads_dir: Path) -> None:
        self._uploads_dir = uploads_dir

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory or not str(event.src_path).endswith(".json"):
            return
        self._handle_sidecar(Path(str(event.src_path)))

    def _handle_sidecar(self, sidecar_path: Path) -> None:
        try:
            metadata: dict[str, Any] = json.loads(sidecar_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("watcher.invalid_sidecar", path=str(sidecar_path), error=str(exc))
            return

        try:
            document_id = metadata["documentId"]
            collection_id = metadata["collectionId"]
            filename = metadata["filename"]
        except KeyError as exc:
            logger.error("watcher.missing_field", path=str(sidecar_path), field=str(exc))
            return
        correlation_id = metadata.get("correlationId", document_id)

        binary_path = self._uploads_dir / f"{document_id}__{filename}"
        if not binary_path.exists():
            logger.error("watcher.missing_binary", document_id=document_id, expected_path=str(binary_path))
            return

        settings = get_settings()
        get_queue().enqueue(
            ingest_document_job,
            document_id=document_id,
            collection_id=collection_id,
            file_path=str(binary_path),
            filename=filename,
            correlation_id=correlation_id,
            sidecar_path=str(sidecar_path),
            retry=Retry(max=settings.max_retries, interval=settings.retry_backoff_seconds),
        )
        logger.info("watcher.enqueued", document_id=document_id, filename=filename)


def start_watching(uploads_dir: str) -> BaseObserver:
    path = Path(uploads_dir)
    path.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(UploadSidecarHandler(path), str(path), recursive=False)
    observer.start()
    return observer
