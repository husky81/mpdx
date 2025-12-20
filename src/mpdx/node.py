

from dataclasses import dataclass, field


@dataclass
class MpdxNode:
    id: str
    parents: list[str]
    type: str            # "table", "title", "t", "v"
    text: str | None = None

    #non-semantic, non-canonical, auxiliary data
    meta: dict = field(default_factory=dict)

