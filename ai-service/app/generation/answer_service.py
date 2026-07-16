import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.embeddings.embedder import embed_query
from app.generation.extractive import extractive_answer
from app.generation.llm import generate_answer
from app.logging import get_logger
from app.retrieval.reranker import rerank
from app.retrieval.vector_store import RetrievedChunk, similarity_search
from app.schemas import Citation

logger = get_logger(__name__)


@dataclass(frozen=True)
class AnswerResult:
    answer: str
    mode: str
    chunks: list[RetrievedChunk]


async def answer_question(
    session: AsyncSession,
    question: str,
    collection_id: uuid.UUID | None,
    top_k: int,
) -> AnswerResult:
    """Retrieve -> rerank -> generate. This is the single-question core the agent's
    `search_documents` tool and the plain `/query` endpoint both call.
    """
    settings = get_settings()
    query_embedding = embed_query(question)
    candidates = await similarity_search(session, query_embedding, settings.retrieval_top_k, collection_id)
    top_chunks = rerank(question, candidates, top_k)

    if settings.generation_mode == "extractive":
        return AnswerResult(answer=extractive_answer(top_chunks), mode="extractive", chunks=top_chunks)

    try:
        answer = await generate_answer(question, top_chunks)
        return AnswerResult(answer=answer, mode=settings.generation_mode, chunks=top_chunks)
    except Exception as exc:
        # An LLM-provider failure (network, auth, rate limit, ...) degrades to extractive mode
        # instead of surfacing a 500 - the fallback is the answer, not an error page.
        logger.warning("generation.llm_failed_fallback_to_extractive", error=str(exc))
        return AnswerResult(answer=extractive_answer(top_chunks), mode="extractive_fallback", chunks=top_chunks)


def to_citations(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            document_id=chunk.document_id,
            filename=chunk.filename,
            page_number=chunk.page_number,
            chunk_index=chunk.chunk_index,
            snippet=chunk.content[:320],
            score=chunk.score,
        )
        for chunk in chunks
    ]
