from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache
def _model() -> SentenceTransformer:
    """Loads the local embedding model once per process.

    all-MiniLM-L6-v2 is ~90MB, CPU-friendly, and produces 384-dim vectors -
    good enough retrieval quality for technical docs without needing a GPU
    or any API key. Cached with lru_cache so the (relatively slow) model
    load only happens once per process, not per request.
    """
    return SentenceTransformer(get_settings().embedding_model_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    vectors = _model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [vector.tolist() for vector in vectors]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
