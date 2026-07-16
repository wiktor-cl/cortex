import uuid

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: uuid.UUID
    filename: str
    page_number: int | None = None
    chunk_index: int
    snippet: str
    score: float


class SubAnswer(BaseModel):
    sub_question: str
    tool_used: str
    answer: str
    citations: list[Citation]


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    collection_id: uuid.UUID | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    answer: str
    mode: str
    citations: list[Citation]
    sub_answers: list[SubAnswer] = Field(default_factory=list)


class IngestResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    chunk_count: int
    content_hash: str
    duplicate_of: uuid.UUID | None = None


class DocumentStatus(BaseModel):
    document_id: uuid.UUID
    status: str
    chunk_count: int
    content_hash: str
    error_message: str | None = None
