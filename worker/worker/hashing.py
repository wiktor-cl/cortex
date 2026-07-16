import hashlib
from pathlib import Path


def content_hash(path: Path) -> str:
    """SHA-256 of the file's bytes - the same idempotency key ai-service enforces server-side.
    Computing it here too lets the job skip the (potentially large) upload entirely for a known
    duplicate instead of relying solely on the server-side unique constraint.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()
