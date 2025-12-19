# mpdx/__init__.py

from .__version__ import __version__
from .parser import parse_mpdx
from .mpis import MPIS
from .kan import Kan, KanType

from .document import load


from .document import MpdxDocument

def from_html(path_or_html: str) -> MpdxDocument:
    """
    Load an HTML table and return an MPDX document.
    """
    raise NotImplementedError(
        "MPDX is in early draft stage. HTML support is not yet implemented."
    )

    return load_html_table(path_or_html)
