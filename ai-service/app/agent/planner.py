import re
from dataclasses import dataclass

_GREETING_PATTERN = re.compile(
    r"^\s*(cze[śs][ćc]|hej|witaj|hello|hi|kim jeste[śs]|who are you)\b", re.IGNORECASE
)
_COMPARISON_KEYWORD = re.compile(r"\b(por[oó]wn\w*|compare|r[oó][żz]nic\w*|difference between)\b", re.IGNORECASE)
_COMPARISON_SPLIT = re.compile(r"\s+(?:vs\.?|versus|\bz\b|\bi\b|\boraz\b|\band\b)\s+", re.IGNORECASE)
_COMPOUND_SPLIT = re.compile(r";|\?\s+|\s+oraz\s+|\s+and\s+then\s+")


@dataclass(frozen=True)
class PlannedStep:
    sub_question: str
    tool_name: str


def split_comparison_question(question: str) -> tuple[str, str] | None:
    """Splits "compare A and B" style questions into their two sides.

    A best-effort regex heuristic, not an NLP parser - it is deliberately simple and fully
    deterministic so the agent works identically with or without an LLM key. If a key is configured,
    an LLM-based planner could replace this function without changing the Tool interface it feeds.
    """
    without_keyword = _COMPARISON_KEYWORD.sub("", question).strip(" ?.")
    parts = [part.strip(" ?.") for part in _COMPARISON_SPLIT.split(without_keyword, maxsplit=1)]
    if len(parts) == 2 and all(parts):
        return parts[0], parts[1]
    return None


def plan(question: str) -> list[PlannedStep]:
    """Decomposes a question into ordered (sub_question, tool) steps.

    Three tools are available - search_documents, answer_directly, compare_sections - see
    app/agent/tools.py. This planner picks between them with readable rules:
      1. Small talk / meta questions never touch the document store.
      2. A question containing a comparison keyword goes to compare_sections as a single step; that
         tool is responsible for splitting and re-combining both sides.
      3. A genuinely compound question ("What is X? Also, how do I do Y?") is split into independent
         search_documents steps, each answered and cited on its own.
      4. Anything else is a single search_documents step.
    """
    stripped = question.strip()

    if _GREETING_PATTERN.match(stripped):
        return [PlannedStep(sub_question=stripped, tool_name="answer_directly")]

    if _COMPARISON_KEYWORD.search(stripped) and split_comparison_question(stripped) is not None:
        return [PlannedStep(sub_question=stripped, tool_name="compare_sections")]

    segments = [segment.strip(" ?.") for segment in _COMPOUND_SPLIT.split(stripped) if segment.strip(" ?.")]
    if len(segments) > 1:
        return [PlannedStep(sub_question=segment, tool_name="search_documents") for segment in segments]

    return [PlannedStep(sub_question=stripped, tool_name="search_documents")]
