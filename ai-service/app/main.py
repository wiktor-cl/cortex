import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app
from sqlalchemy import text

from app.config import get_settings
from app.db import get_engine
from app.logging import configure_logging, correlation_id_var, get_logger
from app.models import Base
from app.routers import documents, health, query

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    configure_logging(get_settings().log_level)
    engine = get_engine()
    async with engine.begin() as connection:
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS rag"))
        await connection.run_sync(Base.metadata.create_all)
    logger.info("startup.complete", generation_mode=get_settings().generation_mode)
    yield


app = FastAPI(title="Cortex AI Service", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Reads X-Correlation-Id set by the gateway (or mints one if called directly, e.g. in tests)
    and binds it to a contextvar for the duration of the request so every log line emitted while
    handling it - including from deep inside the retrieval/generation pipeline - carries the same
    id the gateway logged, making a single user request traceable across both services.
    """
    header_name = get_settings().correlation_id_header
    correlation_id = request.headers.get(header_name) or str(uuid.uuid4())
    token = correlation_id_var.set(correlation_id)
    start = time.perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        response.headers[header_name] = correlation_id
        return response
    finally:
        correlation_id_var.reset(token)


app.include_router(health.router)
app.include_router(query.router)
app.include_router(documents.router)
app.mount("/metrics", make_asgi_app())
