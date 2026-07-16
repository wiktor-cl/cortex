import uuid

from app.config import get_settings
from app.retrieval.reranker import rerank
from app.retrieval.vector_store import RetrievedChunk


def _chunk(text: str, score: float) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        filename="doc.pdf",
        content=text,
        page_number=1,
        chunk_index=0,
        score=score,
    )


def test_rerank_empty_candidates_returns_empty() -> None:
    assert rerank("any query", [], top_k=5) == []


def test_rerank_respects_top_k() -> None:
    candidates = [_chunk(f"passage number {i} about compressors", 0.5) for i in range(10)]

    results = rerank("compressor maintenance", candidates, top_k=3)

    assert len(results) == 3


def test_rerank_prefers_more_relevant_passage() -> None:
    candidates = [
        _chunk("Maximum torque for the M6 bolt is 12 Nm.", 0.5),
        _chunk("Recipe for chocolate chip cookies with sea salt.", 0.5),
    ]

    results = rerank("what is the max torque for the M6 bolt", candidates, top_k=2)

    assert results[0].content.startswith("Maximum torque")


def test_rerank_disabled_falls_back_to_original_order(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(get_settings(), "reranker_enabled", False)

    candidates = [_chunk("first", 0.9), _chunk("second", 0.1)]

    results = rerank("irrelevant query", candidates, top_k=1)

    assert results == candidates[:1]
