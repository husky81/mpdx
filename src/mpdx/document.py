from dataclasses import dataclass


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
