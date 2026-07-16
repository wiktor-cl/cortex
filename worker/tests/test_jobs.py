from pathlib import Path
from unittest.mock import MagicMock

from worker.jobs import ingest_document_job


def test_ingest_document_job_calls_ai_service_and_reports_status(tmp_path: Path) -> None:
    file_path = tmp_path / "manual.txt"
    file_path.write_text("Some content")

    ai_client = MagicMock()
    ai_client.find_by_hash.return_value = None
    ai_client.ingest.return_value = {
        "document_id": "doc-1",
        "status": "DONE",
        "chunk_count": 3,
        "content_hash": "abc",
        "duplicate_of": None,
    }
    gateway_client = MagicMock()

    result = ingest_document_job(
        document_id="doc-1",
        collection_id="col-1",
        file_path=str(file_path),
        filename="manual.txt",
        correlation_id="corr-1",
        ai_client=ai_client,
        gateway_client=gateway_client,
    )

    assert result["status"] == "DONE"
    ai_client.ingest.assert_called_once()
    gateway_client.update_status.assert_called_once_with("doc-1", "DONE", 3, None, "corr-1")
    assert not file_path.exists()


def test_ingest_document_job_skips_upload_when_duplicate_found(tmp_path: Path) -> None:
    file_path = tmp_path / "manual.txt"
    file_path.write_text("Some content")

    ai_client = MagicMock()
    ai_client.find_by_hash.return_value = {
        "document_id": "existing-id",
        "status": "DONE",
        "chunk_count": 5,
        "content_hash": "abc",
        "error_message": None,
    }
    gateway_client = MagicMock()

    result = ingest_document_job(
        document_id="doc-2",
        collection_id="col-1",
        file_path=str(file_path),
        filename="manual.txt",
        correlation_id="corr-1",
        ai_client=ai_client,
        gateway_client=gateway_client,
    )

    ai_client.ingest.assert_not_called()
    gateway_client.update_status.assert_called_once_with("doc-2", "DONE", 5, None, "corr-1")
    assert result["document_id"] == "existing-id"


def test_ingest_document_job_cleans_up_binary_and_sidecar(tmp_path: Path) -> None:
    file_path = tmp_path / "manual.txt"
    file_path.write_text("content")
    sidecar_path = tmp_path / "manual.json"
    sidecar_path.write_text("{}")

    ai_client = MagicMock()
    ai_client.find_by_hash.return_value = None
    ai_client.ingest.return_value = {
        "document_id": "doc-3",
        "status": "DONE",
        "chunk_count": 1,
        "content_hash": "x",
        "duplicate_of": None,
    }
    gateway_client = MagicMock()

    ingest_document_job(
        document_id="doc-3",
        collection_id="col-1",
        file_path=str(file_path),
        filename="manual.txt",
        correlation_id="corr-1",
        sidecar_path=str(sidecar_path),
        ai_client=ai_client,
        gateway_client=gateway_client,
    )

    assert not file_path.exists()
    assert not sidecar_path.exists()


def test_ingest_document_job_reports_failed_status(tmp_path: Path) -> None:
    file_path = tmp_path / "bad.exe"
    file_path.write_bytes(b"binary")

    ai_client = MagicMock()
    ai_client.find_by_hash.return_value = None
    ai_client.ingest.return_value = {
        "document_id": "doc-4",
        "status": "FAILED",
        "chunk_count": 0,
        "content_hash": "x",
        "error_message": "Unsupported file type",
    }
    gateway_client = MagicMock()

    result = ingest_document_job(
        document_id="doc-4",
        collection_id="col-1",
        file_path=str(file_path),
        filename="bad.exe",
        correlation_id="corr-1",
        ai_client=ai_client,
        gateway_client=gateway_client,
    )

    assert result["status"] == "FAILED"
    gateway_client.update_status.assert_called_once_with("doc-4", "FAILED", 0, "Unsupported file type", "corr-1")
