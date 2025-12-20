# src/mpdx/io/mpdx.py

from pathlib import Path
from typing import Union
import json

from mpdx.document import MpdxDocument
from mpdx.node import MpdxNode


HEADER = ["id", "parents", "type", "text", "meta"]


def print_mpdx(self):
    pass

def save_mpdx(doc: MpdxDocument, path: Union[str, Path]) -> None:
    """
    Save an MpdxDocument to a .mpdx file (TSV-based).

    This is a v0 reference serialization.
    """
    path = Path(path)

    if path.suffix != ".mpdx":
        raise ValueError("MPDX files must have a .mpdx extension")

    with path.open("w", encoding="utf-8", newline="") as f:
        # header
        f.write("\t".join(HEADER) + "\n")

        for node in doc.nodes.values():
            _write_node(f, node)

def _write_node(f, node: MpdxNode) -> None:
    parents = ",".join(node.parents) if node.parents else ""
    text = node.text if node.text is not None else ""
    meta = json.dumps(node.meta, ensure_ascii=False)

    row = [
        node.id,
        parents,
        node.type,
        text.replace("\t", " "),  # TSV 보호
        meta,
    ]

    f.write("\t".join(row) + "\n")
