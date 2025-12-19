from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple

class KanType(Enum):
    Table = auto()
    Title = auto()
    Text = auto()      # 일반 텍스트 노드 (t)
    Value = auto()     # 값 노드 (v)

@dataclass(frozen=True)
class Kan:
    id: int
    type: KanType
    parents: Tuple[int, ...]
    text: str = ""