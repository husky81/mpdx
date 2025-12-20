from __future__ import annotations

from typing import Optional, List

from mpdx.document import MpdxDocument
from mpdx.layout.ctl import CanonicalTableLayout, Cell


def mpdx_to_ctl(doc: MpdxDocument) -> CanonicalTableLayout:
    """
    Convert MPDX (layout-preserving v0) back into CTL.

    Assumptions (v0):
    - There is a single root table node with type="table"
    - Cell-like nodes are stored as type="t" (and optionally "v" later)
    - Layout info is preserved in node.meta: row, col, rowspan, colspan, is_header, attrs
    """
    root = doc.root
    if root is None or root.type != "table":
        raise ValueError("MPDX document has no root table node (type='table').")

    n_rows = int(root.meta.get("n_rows", 0) or 0)
    n_cols = int(root.meta.get("n_cols", 0) or 0)

    # Collect cell nodes (v0: we treat "t" as renderable cells; later you may include "v")
    cell_nodes = [n for n in doc.nodes.values() if n.type in {"t"}]

    cells: List[Cell] = []
    owner: List[List[Optional[str]]] = [[None for _ in range(n_cols)] for _ in range(n_rows)]

    # Build CTL cells from meta
    for n in cell_nodes:
        meta = n.meta or {}
        row = int(meta.get("row", 0))
        col = int(meta.get("col", 0))
        rowspan = int(meta.get("rowspan", 1))
        colspan = int(meta.get("colspan", 1))
        is_header = bool(meta.get("is_header", False))
        attrs = meta.get("attrs", {}) or {}

        # Minimal bounds safety
        if row < 0 or col < 0:
            continue
        if n_rows and row >= n_rows:
            continue
        if n_cols and col >= n_cols:
            continue

        # CTL Cell id should be stable; you can keep n.id
        cell = Cell(
            id=n.id,
            row=row,
            col=col,
            rowspan=max(1, rowspan),
            colspan=max(1, colspan),
            text=n.text or "",
            is_header=is_header,
            attrs=attrs,
        )
        cells.append(cell)

        # Fill owner grid
        for r in range(row, min(row + cell.rowspan, n_rows)):
            for c in range(col, min(col + cell.colspan, n_cols)):
                owner[r][c] = cell.id

    # If n_rows/n_cols are missing, infer from cells (fallback)
    if n_rows == 0 or n_cols == 0:
        if not cells:
            return CanonicalTableLayout(n_rows=0, n_cols=0, cells=[], owner=[])
        max_r = max(c.row + c.rowspan for c in cells)
        max_c = max(c.col + c.colspan for c in cells)
        n_rows = max_r
        n_cols = max_c
        owner = [[None for _ in range(n_cols)] for _ in range(n_rows)]
        for c in cells:
            for r in range(c.row, c.row + c.rowspan):
                for cc in range(c.col, c.col + c.colspan):
                    owner[r][cc] = c.id

    return CanonicalTableLayout(
        n_rows=n_rows,
        n_cols=n_cols,
        cells=cells,
        owner=owner,
    )
