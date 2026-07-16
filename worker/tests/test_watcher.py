import json
from pathlib import Path

import fakeredis
import pytest
from rq import Queue
from watchdog.events import DirCreatedEvent, FileCreatedEvent

import worker.watcher as watcher_module
from worker.watcher import UploadSidecarHandler


def _fake_queue() -> Queue:
    return Queue(connection=fakeredis.FakeStrictRedis())


def test_handle_sidecar_enqueues_job_when_binary_exists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_queue = _fake_queue()
    monkeypatch.setattr(watcher_module, "get_queue", lambda: fake_queue)

    document_id = "11111111-1111-1111-1111-111111111111"
    (tmp_path / f"{document_id}__manual.txt").write_text("content")
    sidecar_path = tmp_path / f"{document_id}.json"
    sidecar_path.write_text(
        json.dumps(
            {"documentId": document_id, "collectionId": "c1", "filename": "manual.txt", "correlationId": "corr-1"}
        )
    )

    UploadSidecarHandler(tmp_path)._handle_sidecar(sidecar_path)

    assert len(fake_queue) == 1
    job = fake_queue.jobs[0]
    assert job.kwargs["document_id"] == document_id
    assert job.kwargs["filename"] == "manual.txt"
    assert job.kwargs["correlation_id"] == "corr-1"


def test_handle_sidecar_skips_when_binary_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_queue = _fake_queue()
    monkeypatch.setattr(watcher_module, "get_queue", lambda: fake_queue)

    document_id = "22222222-2222-2222-2222-222222222222"
    sidecar_path = tmp_path / f"{document_id}.json"
    sidecar_path.write_text(json.dumps({"documentId": document_id, "collectionId": "c1", "filename": "missing.txt"}))

    UploadSidecarHandler(tmp_path)._handle_sidecar(sidecar_path)

    assert len(fake_queue) == 0


def test_handle_sidecar_skips_invalid_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_queue = _fake_queue()
    monkeypatch.setattr(watcher_module, "get_queue", lambda: fake_queue)

    sidecar_path = tmp_path / "broken.json"
    sidecar_path.write_text("not json")

    UploadSidecarHandler(tmp_path)._handle_sidecar(sidecar_path)

    assert len(fake_queue) == 0


def test_handle_sidecar_skips_missing_required_field(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_queue = _fake_queue()
    monkeypatch.setattr(watcher_module, "get_queue", lambda: fake_queue)

    sidecar_path = tmp_path / "incomplete.json"
    sidecar_path.write_text(json.dumps({"documentId": "id-only"}))

    UploadSidecarHandler(tmp_path)._handle_sidecar(sidecar_path)

    assert len(fake_queue) == 0


def test_on_created_ignores_non_json_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_queue = _fake_queue()
    monkeypatch.setattr(watcher_module, "get_queue", lambda: fake_queue)
    handler = UploadSidecarHandler(tmp_path)

    event = FileCreatedEvent(str(tmp_path / "some-binary-file.txt"))
    handler.on_created(event)

    assert len(fake_queue) == 0


def test_on_created_ignores_directories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_queue = _fake_queue()
    monkeypatch.setattr(watcher_module, "get_queue", lambda: fake_queue)
    handler = UploadSidecarHandler(tmp_path)

    event = DirCreatedEvent(str(tmp_path / "some-dir.json"))
    handler.on_created(event)

    assert len(fake_queue) == 0
