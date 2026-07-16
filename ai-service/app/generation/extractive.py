from app.retrieval.vector_store import RetrievedChunk

_MAX_SNIPPET_CHARS = 320


def _snippet(text: str) -> str:
    text = " ".join(text.split())
    if len(text) <= _MAX_SNIPPET_CHARS:
        return text
    return text[:_MAX_SNIPPET_CHARS].rsplit(" ", 1)[0] + "…"


def extractive_answer(chunks: list[RetrievedChunk]) -> str:
    """Builds an answer with no LLM at all: the highest-scoring passages, verbatim, with citations.

    This is the mode the whole system runs in when no OPENAI_API_KEY/ANTHROPIC_API_KEY is configured.
    It is deliberately not a "degraded" experience framed as an apology - a service engineer asking
    "what's the max torque for the M6 bolt" is well served by the literal sentence from the manual with
    its page number, arguably better served than by a paraphrase. It is also what makes the whole
    system - including the agent and the full retrieval/reranking pipeline - testable end-to-end
    without any external dependency or API key.
    """
    if not chunks:
        return "Nie znalazłem żadnego fragmentu dokumentacji pasującego do tego pytania."

    lines = ["Na podstawie dokumentacji:"]
    for position, chunk in enumerate(chunks, start=1):
        location = f"{chunk.filename}" + (f", str. {chunk.page_number}" if chunk.page_number else "")
        lines.append(f"[{position}] ({location}) {_snippet(chunk.content)}")
    return "\n".join(lines)
