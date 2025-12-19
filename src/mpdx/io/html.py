# src\mpdx\io\html.py
# from_html(), to_html() entry

from pathlib import Path
from typing import IO, Union


def from_html(path_or_html: str):
    html = read_html(path_or_html)
    ctl = parse_html_to_ctl(html)
    mpdx = ctl_to_mpdx(ctl)
    return mpdx


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
