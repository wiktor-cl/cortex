import uuid

import pytest

from app.agent import tools as tools_module
from app.agent.agent import run_agent
from app.generation.answer_service import AnswerResult
from app.retrieval.vector_store import RetrievedChunk


class _FakeSession:
    """Never touched by these tests - answer_question itself is monkeypatched out."""


def _fake_chunk(text: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        filename="doc.pdf",
        content=text,
        page_number=1,
        chunk_index=0,
        score=0.5,
    )


async def test_run_agent_single_question_uses_search_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_answer_question(session, question, collection_id, top_k):  # type: ignore[no-untyped-def]
        return AnswerResult(answer=f"answer to: {question}", mode="extractive", chunks=[_fake_chunk("fact")])

    monkeypatch.setattr(tools_module, "answer_question", fake_answer_question)

    result = await run_agent(_FakeSession(), "What is the max torque?", None, top_k=5)  # type: ignore[arg-type]

    assert result.mode == "extractive"
    assert "answer to: What is the max torque?" in result.answer
    assert len(result.citations) == 1
    assert result.sub_answers == []


async def test_run_agent_greeting_skips_retrieval_entirely(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fail_if_called(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("retrieval should not be called for small talk")

    monkeypatch.setattr(tools_module, "answer_question", fail_if_called)

    result = await run_agent(_FakeSession(), "Cześć!", None, top_k=5)  # type: ignore[arg-type]

    assert result.mode == "direct"
    assert result.citations == []


async def test_run_agent_compound_question_produces_one_sub_answer_per_part(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_answer_question(session, question, collection_id, top_k):  # type: ignore[no-untyped-def]
        return AnswerResult(answer=f"answer to: {question}", mode="extractive", chunks=[_fake_chunk(question)])

    monkeypatch.setattr(tools_module, "answer_question", fake_answer_question)

    result = await run_agent(_FakeSession(), "What is X?; How does Y work?", None, top_k=5)  # type: ignore[arg-type]

    assert result.mode == "agent_decomposed"
    assert len(result.sub_answers) == 2
    assert len(result.citations) == 2


async def test_run_agent_comparison_merges_both_sides(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_answer_question(session, question, collection_id, top_k):  # type: ignore[no-untyped-def]
        return AnswerResult(answer=f"about {question}", mode="extractive", chunks=[_fake_chunk(question)])

    monkeypatch.setattr(tools_module, "answer_question", fake_answer_question)

    result = await run_agent(_FakeSession(), "Compare procedure A and procedure B", None, top_k=5)  # type: ignore[arg-type]

    assert "about procedure A" in result.answer
    assert "about procedure B" in result.answer
    assert len(result.citations) == 2


async def test_run_agent_deduplicates_repeated_citations_across_sub_answers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    shared_chunk = _fake_chunk("shared fact")

    async def fake_answer_question(session, question, collection_id, top_k):  # type: ignore[no-untyped-def]
        return AnswerResult(answer=f"about {question}", mode="extractive", chunks=[shared_chunk])

    monkeypatch.setattr(tools_module, "answer_question", fake_answer_question)

    result = await run_agent(_FakeSession(), "Compare procedure A and procedure A", None, top_k=5)  # type: ignore[arg-type]

    assert len(result.citations) == 1
