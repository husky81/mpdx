# src/mpdx/__init__.py

from pathlib import Path
from typing import Union

from .__version__ import __version__
from .document import MpdxDocument

from mpdx.io.html import read_html
from mpdx.layout.parser_html import parse_html_to_ctl
from mpdx.convert.ctl_to_mpdx import ctl_to_mpdx
from mpdx.convert.ctl_to_semantic import ctl_to_semantic
from mpdx.convert.semantic_to_mpdx import semantic_to_mpdx

def new() -> MpdxDocument:
    """
    Create an empty MPDX document.
    """
    return MpdxDocument()

def from_html(source: Union[str, Path]) -> MpdxDocument:
    """
    Load an HTML table and return an MPDX document.
    """
    html = read_html(source)
    ctl = parse_html_to_ctl(html)
    #ctl_to_mpdx(ctl)
    semantic = ctl_to_semantic(ctl)
    return semantic_to_mpdx(semantic)


def load(source: Union[str, Path]) -> MpdxDocument:
    """
    Load a document and infer format from file extension.
    """
    path = Path(source)

    if path.suffix.lower() in {".html", ".htm"}:
        return from_html(path)

    elif path.suffix.lower() == ".docx":
        raise NotImplementedError("DOCX support is not implemented yet")

    elif path.suffix.lower() == ".md":
        raise NotImplementedError("Markdown support is not implemented yet")

    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")
