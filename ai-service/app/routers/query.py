import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.agent import run_agent
from app.db import get_session
from app.metrics import QUERY_LATENCY, QUERY_REQUESTS
from app.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(payload: QueryRequest, session: AsyncSession = Depends(get_session)) -> QueryResponse:
    start = time.perf_counter()
    result = await run_agent(session, payload.question, payload.collection_id, payload.top_k)
    QUERY_LATENCY.observe(time.perf_counter() - start)
    QUERY_REQUESTS.labels(mode=result.mode).inc()
    return QueryResponse(
        answer=result.answer,
        mode=result.mode,
        citations=result.citations,
        sub_answers=result.sub_answers,
    )
