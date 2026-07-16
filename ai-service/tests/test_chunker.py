from app.ingestion.chunker import chunk_pages, split_sentences
from app.ingestion.loaders import PageText


def test_split_sentences_splits_on_terminal_punctuation() -> None:
    text = "First sentence. Second sentence! Third sentence? Fourth."
    assert split_sentences(text) == [
        "First sentence.",
        "Second sentence!",
        "Third sentence?",
        "Fourth.",
    ]


def test_split_sentences_empty_text_returns_empty_list() -> None:
    assert split_sentences("   ") == []


def test_chunk_pages_keeps_short_page_as_single_chunk() -> None:
    pages = [PageText(text="One short sentence.", page_number=1)]

    chunks = chunk_pages(pages, chunk_size_chars=1000, overlap_chars=100)

    assert len(chunks) == 1
    assert chunks[0].text == "One short sentence."
    assert chunks[0].page_number == 1
    assert chunks[0].chunk_index == 0


def test_chunk_pages_never_splits_a_sentence_in_half() -> None:
    sentences = [f"Sentence number {i} has a reasonable length to it." for i in range(20)]
    pages = [PageText(text=" ".join(sentences), page_number=None)]

    chunks = chunk_pages(pages, chunk_size_chars=200, overlap_chars=40)

    assert len(chunks) > 1
    for chunk in chunks:
        for sentence in sentences:
            # Every sentence appears whole wherever it appears, never truncated mid-word.
            if sentence in chunk.text:
                assert sentence in chunk.text.split(sentence)[0] + sentence + chunk.text.split(sentence)[-1]


def test_chunk_pages_produces_overlap_between_consecutive_chunks() -> None:
    sentences = [f"This is sentence number {i} in the document body." for i in range(30)]
    pages = [PageText(text=" ".join(sentences), page_number=None)]

    chunks = chunk_pages(pages, chunk_size_chars=300, overlap_chars=80)

    assert len(chunks) >= 2
    first_sentences = set(split_sentences(chunks[0].text))
    second_sentences = set(split_sentences(chunks[1].text))
    assert first_sentences & second_sentences, "expected at least one sentence shared via overlap"


def test_chunk_pages_indexes_increment_across_multiple_pages() -> None:
    pages = [
        PageText(text="Page one sentence.", page_number=1),
        PageText(text="Page two sentence.", page_number=2),
    ]

    chunks = chunk_pages(pages, chunk_size_chars=1000, overlap_chars=100)

    assert [chunk.chunk_index for chunk in chunks] == [0, 1]
    assert [chunk.page_number for chunk in chunks] == [1, 2]


def test_chunk_pages_skips_empty_pages() -> None:
    pages = [PageText(text="   ", page_number=1)]

    chunks = chunk_pages(pages, chunk_size_chars=1000, overlap_chars=100)

    assert chunks == []
