from __future__ import annotations

from html import escape
from typing import Dict, Tuple

from mpdx.layout.ctl import CanonicalTableLayout, Cell


def ctl_to_html(ctl: CanonicalTableLayout) -> str:
    """
    Render CTL to an HTML <table> preserving rowspan/colspan.

    Strategy:
    - For each row/col, render only the top-left occurrence of a merged cell.
    - Skip covered positions using the cell owner's id map.
    """
    # Index cells by (row, col) where they start
    starts: Dict[Tuple[int, int], Cell] = {(c.row, c.col): c for c in ctl.cells}

    lines = []
    lines.append("<table>")

    for r in range(ctl.n_rows):
        lines.append("  <tr>")

        c = 0
        while c < ctl.n_cols:
            cell = starts.get((r, c))
            if cell is None:
                # If this position is covered by a merged cell, skip it.
                owner_id = ctl.owner[r][c] if ctl.owner and r < len(ctl.owner) and c < len(ctl.owner[r]) else None
                if owner_id is not None:
                    c += 1
                    continue
                # Otherwise render an empty td (optional; you can also skip)
                lines.append("    <td></td>")
                c += 1
                continue

            tag = "th" if cell.is_header else "td"

            attrs = []
            if cell.rowspan and cell.rowspan > 1:
                attrs.append(f'rowspan="{cell.rowspan}"')
            if cell.colspan and cell.colspan > 1:
                attrs.append(f'colspan="{cell.colspan}"')

            # Optional: carry through safe attributes from original HTML
            # Avoid duplicating rowspan/colspan
            extra = dict(cell.attrs or {})
            extra.pop("rowspan", None)
            extra.pop("colspan", None)

            # Keep only a small safe subset by default
            for k in ("class", "style"):
                if k in extra and extra[k]:
                    v = escape(str(extra[k]), quote=True)
                    attrs.append(f'{k}="{v}"')

            attr_str = (" " + " ".join(attrs)) if attrs else ""
            text = escape(cell.text or "")

            lines.append(f"    <{tag}{attr_str}>{text}</{tag}>")

            # Move to next column; merged cells occupy colspan columns
            c += max(1, cell.colspan)

        lines.append("  </tr>")

    lines.append("</table>")
    return "\n".join(lines)
