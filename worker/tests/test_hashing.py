from pathlib import Path

from worker.hashing import content_hash


def test_content_hash_deterministic(tmp_path: Path) -> None:
    file_path = tmp_path / "a.txt"
    file_path.write_bytes(b"hello")

    assert content_hash(file_path) == content_hash(file_path)


def test_content_hash_differs_for_different_content(tmp_path: Path) -> None:
    first = tmp_path / "a.txt"
    first.write_bytes(b"hello")
    second = tmp_path / "b.txt"
    second.write_bytes(b"world")

    assert content_hash(first) != content_hash(second)
