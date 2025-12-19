@dataclass
class MpdxNode:
    id: str
    type: str            # "table", "title", "t", "v"
    parents: list[str]
    text: str | None = None
    meta: dict = field(default_factory=dict)

