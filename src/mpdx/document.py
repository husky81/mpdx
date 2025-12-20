# src/mpdx/document.py


from dataclasses import dataclass, field
from typing import Dict, Optional
from .node import MpdxNode


@dataclass
class MpdxDocument:
    nodes: Dict[str, MpdxNode] = field(default_factory=dict)
    root_id: Optional[str] = None

    def add_node(self, node: MpdxNode):
        self.nodes[node.id] = node

    def get_node(self, node_id: str) -> Optional[MpdxNode]:
        return self.nodes.get(node_id)

    @property
    def root(self) -> Optional[MpdxNode]:
        return self.nodes.get(self.root_id) if self.root_id else None

    # ---------- human-friendly print ----------
    def __str__(self) -> str:
        """
        TSV preview for humans.
        Columns: id, parents, type, text
        parents is always shown as a list: [], [p1], [p1, p2]
        """
        lines: list[str] = []
        lines.append("\t".join(["id", "parents", "type", "text"]))

        for node in self.nodes.values():
            # parents formatting (always explicit)
            if node.parents:
                parents_repr = "[" + ", ".join(node.parents) + "]"
            else:
                parents_repr = "[]"

            text = node.text or ""
            text = text.replace("\t", " ").replace(
                "\r", " ").replace("\n", " ")

            lines.append(
                "\t".join([
                    str(node.id),
                    parents_repr,
                    node.type,
                    text,
                ])
            )

        return "\n".join(lines)

    def find(self, *, type=None, text=None):
        for node in self.nodes.values():
            if type is not None and node.type != type:
                continue
            if text is not None and node.text != text:
                continue
            yield node


    # ---------- serialization ----------
    def save(self, path):
        # local import to avoid circular imports
        from mpdx.io.mpdx import save_mpdx
        save_mpdx(self, path)

    def save_html(self, path):
        from mpdx.io.html import save_html
        save_html(self, path)

    # ---------- rendering ----------
    def to_html(self) -> str:
        """Render document back to HTML table (v0: layout-preserving)."""
        # local import to avoid circular imports
        from mpdx.convert.mpdx_to_ctl import mpdx_to_ctl
        from mpdx.render.html import ctl_to_html

        ctl = mpdx_to_ctl(self)
        return ctl_to_html(ctl)


