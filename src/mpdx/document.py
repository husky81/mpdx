from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Dict, Optional
from mpdx.node import MpdxNode

@dataclass
class MpdxDocument:
    nodes: Dict[str, MpdxNode] = field(default_factory=dict)
    root_id: Optional[str] = None

    def add_node(self, node: MpdxNode):
        self.nodes[node.id] = node
        
    def get_node(self, node_id: str) -> MpdxNode: ...

    def to_html(self) -> str:
        """Render document back to HTML table."""

    def find(self, *, type=None, text=None):
        """Query nodes by simple conditions."""

    @property
    def root(self) -> Optional[MpdxNode]:
        if self.root_id is None:
            return None
        return self.nodes.get(self.root_id)

    def save(self, path):
        from mpdx.io.mpdx import save_mpdx
        save_mpdx(self, path)

    def print(self):
        from mpdx.io.mpdx import print_mpdx
        print_mpdx(self)