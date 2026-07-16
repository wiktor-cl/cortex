from app.ingestion.hashing import content_hash


def test_content_hash_is_deterministic() -> None:
    assert content_hash(b"same bytes") == content_hash(b"same bytes")


def test_content_hash_differs_for_different_content() -> None:
    assert content_hash(b"content a") != content_hash(b"content b")
