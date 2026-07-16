import re
from dataclasses import dataclass

from app.ingestion.loaders import PageText

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class TextChunk:
    text: str
    page_number: int | None
    chunk_index: int


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [sentence.strip() for sentence in _SENTENCE_BOUNDARY.split(text) if sentence.strip()]


def chunk_pages(pages: list[PageText], chunk_size_chars: int, overlap_chars: int) -> list[TextChunk]:
    """Group sentences into ~chunk_size_chars chunks, carrying a sentence-level overlap forward.

    Splitting on sentence boundaries (instead of a raw character window) avoids cutting a
    citation-worthy sentence in half. The overlap exists so that a fact stated right at a chunk
    boundary is still fully present in at least one chunk's embedding - without it, a query whose
    answer straddles two chunks could retrieve neither with high similarity. We deliberately never
    split a single sentence that is itself longer than chunk_size_chars: preserving the sentence
    boundary is worth an occasional oversized chunk.
    """
    chunks: list[TextChunk] = []
    index = 0

    for page in pages:
        sentences = split_sentences(page.text)
        current: list[str] = []
        current_len = 0
        i = 0
        while i < len(sentences):
            sentence = sentences[i]
            if current and current_len + len(sentence) + 1 > chunk_size_chars:
                chunks.append(TextChunk(text=" ".join(current), page_number=page.page_number, chunk_index=index))
                index += 1
                current, current_len = _build_overlap_tail(current, overlap_chars)
                continue
            current.append(sentence)
            current_len += len(sentence) + 1
            i += 1

        if current:
            chunks.append(TextChunk(text=" ".join(current), page_number=page.page_number, chunk_index=index))
            index += 1

    return chunks


def _build_overlap_tail(current: list[str], overlap_chars: int) -> tuple[list[str], int]:
    tail: list[str] = []
    tail_len = 0
    for sentence in reversed(current):
        if tail_len + len(sentence) > overlap_chars:
            break
        tail.insert(0, sentence)
        tail_len += len(sentence) + 1
    return tail, tail_len
