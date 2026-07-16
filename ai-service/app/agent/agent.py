import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.planner import plan
from app.agent.tools import AnswerDirectlyTool, CompareSectionsTool, SearchDocumentsTool, Tool
from app.config import get_settings
from app.schemas import Citation, SubAnswer

_TOOL_REGISTRY: dict[str, Tool] = {
    tool.name: tool
    for tool in (SearchDocumentsTool(), AnswerDirectlyTool(), CompareSectionsTool())
}


@dataclass(frozen=True)
class AgentResult:
    answer: str
    mode: str
    citations: list[Citation]
    sub_answers: list[SubAnswer]


async def run_agent(
    session: AsyncSession, question: str, collection_id: uuid.UUID | None, top_k: int
) -> AgentResult:
    """Plan -> pick a tool per step -> execute -> merge. Single-step questions (the common case)
    return the tool's answer directly; multi-step ones get an explicit sub_answers breakdown so the
    frontend can show which sub-question produced which citation.
    """
    steps = plan(question)
    sub_answers = []
    for step in steps:
        tool = _TOOL_REGISTRY[step.tool_name]
        result = await tool.run(session, step.sub_question, collection_id, top_k)
        sub_answers.append(
            SubAnswer(
                sub_question=step.sub_question,
                tool_used=step.tool_name,
                answer=result.answer,
                citations=result.citations,
            )
        )

    if len(sub_answers) == 1:
        only = sub_answers[0]
        mode = "direct" if only.tool_used == "answer_directly" else get_settings().generation_mode
        # A single step can still carry duplicate citations - compare_sections runs two searches
        # and merges them itself without deduping, so dedup is applied uniformly here regardless
        # of how many steps the plan produced.
        return AgentResult(answer=only.answer, mode=mode, citations=_deduplicate(only.citations), sub_answers=[])

    combined_answer = "\n\n".join(
        f"{index}. {sub.sub_question}\n{sub.answer}" for index, sub in enumerate(sub_answers, start=1)
    )
    combined_citations = _deduplicate([citation for sub in sub_answers for citation in sub.citations])
    return AgentResult(
        answer=combined_answer, mode="agent_decomposed", citations=combined_citations, sub_answers=sub_answers
    )


def _deduplicate(citations: list[Citation]) -> list[Citation]:
    seen: set[tuple[uuid.UUID, int]] = set()
    unique: list[Citation] = []
    for citation in citations:
        key = (citation.document_id, citation.chunk_index)
        if key not in seen:
            seen.add(key)
            unique.append(citation)
    return unique
