from dataclasses import dataclass
from pathlib import Path
from typing import Union
from .node import MpdxNode


@dataclass
class MpdxDocument:
    nodes: dict[str, MpdxNode]
    root_id: str

    def add_node(self, node: MpdxNode) -> None: ...
    def get_node(self, node_id: str) -> MpdxNode: ...

    def to_html(self) -> str:
        """Render document back to HTML table."""

    def find(self, *, type=None, text=None):
        """Query nodes by simple conditions."""


def load(source: Union[str, Path]):
    path = Path(source)

    if path.suffix.lower() in {".html", ".htm"}:
        from .io.html import from_html
        return from_html(path)

    elif path.suffix.lower() in {".docx"}:
        return from_docx(path)

    elif path.suffix.lower() in {".md"}:
        return from_markdown(path)

    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")
