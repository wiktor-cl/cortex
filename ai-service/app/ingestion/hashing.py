import hashlib


def content_hash(data: bytes) -> str:
    """SHA-256 of the raw file bytes; the idempotency key used to avoid re-indexing a document."""
    return hashlib.sha256(data).hexdigest()
