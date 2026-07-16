from dataclasses import replace
from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.config import get_settings
from app.retrieval.vector_store import RetrievedChunk


@lru_cache
def _model() -> CrossEncoder:
    return CrossEncoder(get_settings().reranker_model_name)


def rerank(query: str, candidates: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
    """Re-scores retrieval candidates with a cross-encoder for higher precision.

    The bi-encoder used for the initial vector search embeds the query and
    each chunk independently, which is what makes it fast enough to search
    thousands of chunks, but it caps precision because the two texts never
    actually attend to each other. A cross-encoder scores the (query, chunk)
    pair jointly and is meaningfully more accurate, at the cost of not being
    precomputable/indexable - so we over-fetch with the cheap vector search
    (retrieval_top_k) and only spend the cross-encoder's cost narrowing that
    down to the handful of chunks (rerank_top_k) that actually go to
    generation.
    """
    if not candidates:
        return []

    settings = get_settings()
    if not settings.reranker_enabled:
        return candidates[:top_k]

    pairs = [(query, candidate.content) for candidate in candidates]
    scores = _model().predict(pairs)  # type: ignore[arg-type]  # sentence-transformers' stub is overly broad here
    reranked = sorted(zip(candidates, scores, strict=True), key=lambda pair: pair[1], reverse=True)
    return [replace(candidate, score=float(score)) for candidate, score in reranked[:top_k]]
