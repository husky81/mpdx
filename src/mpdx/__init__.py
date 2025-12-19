# mpdx/__init__.py

from .__version__ import __version__

from .parser import parse_mpdx as load
from .mpis import MPIS
from .kan import Kan, KanType


from .document import MpdxDocument
from .io.html import load_html_table

def from_html(path_or_html: str) -> MpdxDocument:
    """
    Load an HTML table and return an MPDX document.
    """
    raise NotImplementedError(
        "MPDX is in early draft stage. HTML support is not yet implemented."
    )

    return load_html_table(path_or_html)
