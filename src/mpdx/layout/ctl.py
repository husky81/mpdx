# src\mpdx\layout\ctl.py
# CanonicalTableLayout

from dataclasses import dataclass, field


@dataclass
class Cell:
    id: str
    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    text: str = ""
    is_header: bool = False
    attrs: dict = field(default_factory=dict)  # scope, headers 등

@dataclass
class CanonicalTableLayout:
    n_rows: int
    n_cols: int
    cells: list[Cell]
    owner: list[list[str]]  # owner[r][c] = cell.id
