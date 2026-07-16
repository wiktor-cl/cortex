from app.config import get_settings
from app.embeddings.embedder import embed_query, embed_texts


def test_embed_texts_returns_correct_dimension_and_count() -> None:
    vectors = embed_texts(["hello world", "another sentence"])

    assert len(vectors) == 2
    assert len(vectors[0]) == get_settings().embedding_dimension


def test_embed_texts_empty_list_returns_empty_list() -> None:
    assert embed_texts([]) == []


def test_embed_query_returns_a_single_vector() -> None:
    vector = embed_query("what is the maximum torque")

    assert len(vector) == get_settings().embedding_dimension


def test_similar_sentences_are_closer_than_unrelated_ones() -> None:
    def dot(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b, strict=True))

    base = embed_query("How do I reset the compressor alarm?")
    similar = embed_query("Steps to clear the compressor alarm")
    unrelated = embed_query("Recipe for chocolate chip cookies")

    # Embeddings are L2-normalized, so the dot product is cosine similarity.
    assert dot(base, similar) > dot(base, unrelated)
