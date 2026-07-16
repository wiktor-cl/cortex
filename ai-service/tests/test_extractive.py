import uuid

from app.generation.extractive import extractive_answer
from app.retrieval.vector_store import RetrievedChunk


def _chunk(text: str, filename: str = "manual.pdf", page: int | None = 3, score: float = 0.9) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        filename=filename,
        content=text,
        page_number=page,
        chunk_index=0,
        score=score,
    )


def test_extractive_answer_with_no_chunks_says_so_in_polish() -> None:
    answer = extractive_answer([])

    assert "Nie znalazłem" in answer


def test_extractive_answer_cites_filename_and_page() -> None:
    answer = extractive_answer([_chunk("Maximum torque is 12 Nm.", filename="bolt-manual.pdf", page=42)])

    assert "bolt-manual.pdf" in answer
    assert "str. 42" in answer
    assert "Maximum torque is 12 Nm." in answer


def test_extractive_answer_omits_page_when_format_has_none() -> None:
    answer = extractive_answer([_chunk("Some markdown fact.", filename="notes.md", page=None)])

    assert "notes.md" in answer
    assert "str." not in answer


def test_extractive_answer_numbers_multiple_citations_in_order() -> None:
    answer = extractive_answer([_chunk("First fact."), _chunk("Second fact.")])

    assert answer.index("[1]") < answer.index("[2]")
    assert answer.index("First fact.") < answer.index("Second fact.")


def test_extractive_answer_truncates_long_snippets_with_ellipsis() -> None:
    long_text = "word " * 200
    answer = extractive_answer([_chunk(long_text)])

    assert "…" in answer
