# src\mpdx\io\html.py

from pathlib import Path
from typing import IO, Union

from mpdx.document import MpdxDocument


def read_html(source: Union[str, Path, IO[str]]) -> str:
    """
    Read HTML content from a file path, raw HTML string,
    or a file-like object, and return it as a normalized string.

    This function does NOT parse or interpret HTML.
    """

    # file-like object (e.g. open file, StringIO)
    if hasattr(source, "read"):
        html = source.read()

    # Path or path-like string
    elif isinstance(source, (str, Path)):
        path = Path(source)

        if path.exists():
            html = path.read_text(encoding="utf-8")
        else:
            # assume raw HTML string
            html = str(source)

    else:
        raise TypeError(f"Unsupported HTML source type: {type(source)}")

    return _normalize_html(html)


def _normalize_html(html: str) -> str:
    """
    Minimal HTML normalization:
    - remove UTF-8 BOM
    - strip leading/trailing whitespace
    """
    return html.lstrip("\ufeff").strip()


def save_html(doc: MpdxDocument, path: Union[str, Path]) -> None:
    """
    Save an MpdxDocument as an HTML file.
    """
    path = Path(path)

    if path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("HTML output file must have .html or .htm extension")

    html = doc.to_html()

    path.write_text(html, encoding="utf-8")