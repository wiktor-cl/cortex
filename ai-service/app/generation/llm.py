from app.config import get_settings
from app.logging import get_logger
from app.retrieval.vector_store import RetrievedChunk

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are Cortex, a technical documentation assistant. Answer strictly using the numbered "
    "context passages below. Cite passages inline as [1], [2], etc. matching their number. If the "
    "passages do not contain the answer, say so plainly instead of guessing."
)


def _build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(
        f"[{i}] (source: {chunk.filename}"
        + (f", page {chunk.page_number}" if chunk.page_number else "")
        + f")\n{chunk.content}"
        for i, chunk in enumerate(chunks, start=1)
    )
    return f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"


async def generate_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    """Calls the configured LLM provider. Only reachable when generation_mode != 'extractive'."""
    settings = get_settings()
    prompt = _build_prompt(question, chunks)

    if settings.generation_mode == "anthropic":
        return await _generate_anthropic(prompt, settings.anthropic_api_key, settings.llm_model_anthropic)
    if settings.generation_mode == "openai":
        return await _generate_openai(prompt, settings.openai_api_key, settings.llm_model_openai)
    raise RuntimeError("generate_answer called without a configured LLM provider")


async def _generate_openai(prompt: str, api_key: str | None, model: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content or ""


async def _generate_anthropic(prompt: str, api_key: str | None, model: str) -> str:
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
