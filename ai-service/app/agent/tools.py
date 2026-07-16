import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.planner import split_comparison_question
from app.generation.answer_service import answer_question, to_citations
from app.schemas import Citation


@dataclass(frozen=True)
class ToolResult:
    answer: str
    citations: list[Citation]


class Tool(ABC):
    """Every agent tool implements this interface, so adding a new one is a matter of
    subclassing, implementing `run`, and registering it in `app/agent/agent.py`'s tool registry -
    the planner and the agent loop don't need to change.
    """

    name: str
    description: str

    @abstractmethod
    async def run(
        self, session: AsyncSession, question: str, collection_id: uuid.UUID | None, top_k: int
    ) -> ToolResult: ...


class SearchDocumentsTool(Tool):
    name = "search_documents"
    description = "Retrieves and answers from the most relevant documentation passages."

    async def run(
        self, session: AsyncSession, question: str, collection_id: uuid.UUID | None, top_k: int
    ) -> ToolResult:
        result = await answer_question(session, question, collection_id, top_k)
        return ToolResult(answer=result.answer, citations=to_citations(result.chunks))


class AnswerDirectlyTool(Tool):
    name = "answer_directly"
    description = "Answers small talk / meta questions about Cortex without querying the document store."

    _CANNED_ANSWER = (
        "Jestem Cortex - asystent dokumentacji technicznej. Zadaj pytanie merytoryczne "
        "(np. o procedurę, parametr lub usterkę), a odpowiem cytatami z zindeksowanych dokumentów."
    )

    async def run(
        self, session: AsyncSession, question: str, collection_id: uuid.UUID | None, top_k: int
    ) -> ToolResult:
        return ToolResult(answer=self._CANNED_ANSWER, citations=[])


class CompareSectionsTool(Tool):
    name = "compare_sections"
    description = "Answers each side of a comparison question independently, then merges both results."

    async def run(
        self, session: AsyncSession, question: str, collection_id: uuid.UUID | None, top_k: int
    ) -> ToolResult:
        sides = split_comparison_question(question)
        if sides is None:
            # Defensive fallback: the planner only routes here when a split succeeded, but the tool
            # must stay correct even if called directly (e.g. from a test or a future caller).
            result = await answer_question(session, question, collection_id, top_k)
            return ToolResult(answer=result.answer, citations=to_citations(result.chunks))

        left_question, right_question = sides
        left = await answer_question(session, left_question, collection_id, top_k)
        right = await answer_question(session, right_question, collection_id, top_k)

        answer = (
            f"Porównanie:\n\n1) {left_question}\n{left.answer}\n\n2) {right_question}\n{right.answer}"
        )
        citations = to_citations(left.chunks) + to_citations(right.chunks)
        return ToolResult(answer=answer, citations=citations)
