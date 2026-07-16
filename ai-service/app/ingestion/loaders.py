from dataclasses import dataclass
from io import BytesIO

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from markdown import markdown
from pypdf import PdfReader


@dataclass(frozen=True)
class PageText:
    """One unit of extracted text plus the page it came from, if the format has pages.

    PDF is the only loader that can report a real page number - it's the
    format service engineers actually cite ("see manual page 42"). Markdown,
    TXT, HTML and DOCX have no reliable page concept, so `page_number` stays
    `None` for them and citations for those formats surface only the
    document + chunk position.
    """

    text: str
    page_number: int | None


class UnsupportedFileTypeError(ValueError):
    def __init__(self, extension: str) -> None:
        super().__init__(f"Unsupported file type: '{extension}'")
        self.extension = extension


def load_pdf(data: bytes) -> list[PageText]:
    reader = PdfReader(BytesIO(data))
    pages = []
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(PageText(text=text, page_number=index + 1))
    return pages


def load_markdown(data: bytes) -> list[PageText]:
    html = markdown(data.decode("utf-8"))
    text = BeautifulSoup(html, "html.parser").get_text(separator=" ")
    return [PageText(text=text, page_number=None)] if text.strip() else []


def load_txt(data: bytes) -> list[PageText]:
    text = data.decode("utf-8")
    return [PageText(text=text, page_number=None)] if text.strip() else []


def load_html(data: bytes) -> list[PageText]:
    text = BeautifulSoup(data, "html.parser").get_text(separator=" ")
    return [PageText(text=text, page_number=None)] if text.strip() else []


def load_docx(data: bytes) -> list[PageText]:
    document = DocxDocument(BytesIO(data))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    return [PageText(text=text, page_number=None)] if text.strip() else []


_LOADERS_BY_EXTENSION = {
    "pdf": load_pdf,
    "md": load_markdown,
    "markdown": load_markdown,
    "txt": load_txt,
    "html": load_html,
    "htm": load_html,
    "docx": load_docx,
}


def load_document(filename: str, data: bytes) -> list[PageText]:
    extension = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    loader = _LOADERS_BY_EXTENSION.get(extension)
    if loader is None:
        raise UnsupportedFileTypeError(extension)
    return loader(data)
