#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mdpx_to_html.py  (MPDX → HTML, row-dimension model)

Model:
- table's children t-nodes define dimensions (row-axis + value-axis)
- row values are chained across row-axis dims:
    first dim value: parents = [dim1]
    next dim value : parents = [prev_value, dimN]
- value columns are leaf nodes under value-axis dims used by v nodes
- cell values come from v nodes with parents [row_leaf, value_col_leaf] (order free)

Usage:
  python mdpx_to_html.py input.mpdx [output.html]
  or import and call main("a.mpdx", "a.html")
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Iterable
import html
import re
import sys


# -----------------------------
# Data model & parsing
# -----------------------------

@dataclass(frozen=True)
class Node:
    id: int
    parents: Tuple[int, ...]
    type: str
    text: str


def parse_parents(raw: str) -> Tuple[int, ...]:
    raw = (raw or "").strip()
    if not raw:
        return tuple()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return tuple()
        return tuple(int(x.strip()) for x in inner.split(",") if x.strip())
    return (int(raw),)


def parse_mpdx_text(path: Path) -> Dict[int, Node]:
    nodes: Dict[int, Node] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        cols = re.split(r"\t+", s)
        if len(cols) < 3:
            continue
        # header skip: "id parents type text"
        if not cols[0].isdigit():
            continue

        nid = int(cols[0])
        parents = parse_parents(cols[1])
        ntype = cols[2].strip()
        text = cols[3].strip() if len(cols) > 3 else ""
        nodes[nid] = Node(nid, parents, ntype, text)
    return nodes


def build_children_single_parent(nodes: Dict[int, Node]) -> Dict[int, List[int]]:
    ch: Dict[int, List[int]] = {}
    for n in nodes.values():
        if len(n.parents) == 1:
            ch.setdefault(n.parents[0], []).append(n.id)
    for k in ch:
        ch[k].sort()
    return ch


def find_first(nodes: Dict[int, Node], ntype: str) -> Node:
    xs = [n for n in nodes.values() if n.type == ntype]
    if not xs:
        raise ValueError(f"No node found: type={ntype}")
    return sorted(xs, key=lambda n: n.id)[0]


# -----------------------------
# Dimension extraction (row-dimension model)
# -----------------------------

def pick_dimension_root_id(nodes: Dict[int, Node]) -> Tuple[int, int]:
    """
    Prefer table as dimension-root parent.
    If table has no t-children, fallback to title as dimension-root parent.
    Returns: (table_id, dim_root_parent_id)
    """
    table = find_first(nodes, "table")
    ch = build_children_single_parent(nodes)

    # table's direct t children?
    table_t_children = [cid for cid in ch.get(
        table.id, []) if nodes[cid].type == "t"]
    if table_t_children:
        return (table.id, table.id)

    # fallback: title's t children
    title = find_first(nodes, "title")
    return (table.id, title.id)


def dimension_roots(nodes: Dict[int, Node], dim_root_parent_id: int) -> List[int]:
    """
    Dimension roots are t nodes with single-parent dim_root_parent_id.
    Ordered by node id.
    """
    ch = build_children_single_parent(nodes)
    dims = [cid for cid in ch.get(
        dim_root_parent_id, []) if nodes[cid].type == "t"]
    dims.sort()
    return dims


def collect_leafs_under(nodes: Dict[int, Node], ch: Dict[int, List[int]], root: int) -> List[int]:
    """
    Collect leaf t-nodes under 'root' by following single-parent edges.
    Leaf means: has no single-parent children of type t.
    """
    out: List[int] = []
    stack = [root]
    while stack:
        cur = stack.pop()
        kids = [k for k in ch.get(cur, []) if nodes[k].type == "t"]
        if not kids:
            out.append(cur)
        else:
            for k in reversed(kids):
                stack.append(k)
    return out


def value_column_leafs_from_v(nodes: Dict[int, Node]) -> Set[int]:
    """
    Any node id that appears in v.parents is a candidate value-column leaf.
    (We'll later map it to a dimension root.)
    """
    leafs: Set[int] = set()
    for n in nodes.values():
        if n.type == "v" and len(n.parents) == 2:
            a, b = n.parents
            leafs.add(a)
            leafs.add(b)
    return leafs


def dim_root_of(nodes: Dict[int, Node], ch: Dict[int, List[int]], dim_roots: List[int], node_id: int) -> Optional[int]:
    """
    If node_id is in the subtree of a dimension root (following single-parent edges), return that root.
    Fast enough for small docs; for bigger, precompute ancestor map.
    """
    # Quick: if node_id is itself a dim root
    if node_id in dim_roots:
        return node_id

    # Build parent->children implies we can BFS from each dim root; do reverse membership test.
    # For simplicity, scan each dim root subtree.
    for dr in dim_roots:
        stack = [dr]
        seen = set()
        while stack:
            cur = stack.pop()
            if cur == node_id:
                return dr
            if cur in seen:
                continue
            seen.add(cur)
            for k in ch.get(cur, []):
                if nodes[k].type == "t":
                    stack.append(k)
    return None


def split_row_dims_and_value_cols(nodes, dim_roots):
    """
    Much looser rule:
    - value columns = leaf t-nodes referenced by v
    - row dimensions = all other t-nodes that are not value columns
    """
    used_by_v = value_column_leafs_from_v(nodes)

    value_cols = sorted(used_by_v)

    row_dims = [
        n.id for n in nodes.values()
        if n.type == "t" and n.id not in value_cols
    ]

    # 안정적인 순서
    row_dims.sort()

    return row_dims, value_cols


# -----------------------------
# Row materialization (chain across row-dims)
# -----------------------------

def build_row_value_index(nodes: Dict[int, Node], row_dims: List[int]) -> Dict[Tuple[Optional[int], int], List[int]]:
    """
    Index row-value nodes by (prev_row_value_id, dim_id) -> [row_value_id...]
    Pattern:
      first dim value: parents == (dim_id,)
      next dim value : parents contains prev_value_id and dim_id (order free) and length == 2
    """
    idx: Dict[Tuple[Optional[int], int], List[int]] = {}

    row_dim_set = set(row_dims)

    for n in nodes.values():
        if n.type != "t":
            continue
        # ignore dimension roots themselves
        if n.id in row_dim_set:
            continue

        ps = n.parents
        if len(ps) == 1 and ps[0] in row_dim_set:
            # first dim value
            idx.setdefault((None, ps[0]), []).append(n.id)
        elif len(ps) == 2:
            a, b = ps
            # one is dim, other is prev value
            if a in row_dim_set and b not in row_dim_set:
                idx.setdefault((b, a), []).append(n.id)
            elif b in row_dim_set and a not in row_dim_set:
                idx.setdefault((a, b), []).append(n.id)

    for k in idx:
        idx[k].sort()
    return idx


def build_rows(nodes: Dict[int, Node], row_dims: List[int], value_cols: List[int]) -> List[Tuple[List[int], int]]:
    """
    Loose row materialization:
    - Any t-node that has at least one v attached becomes a row
    - Row header values are inferred from its ancestors
    """
    # 1. v가 붙은 row node 수집
    value_set = set(value_cols)
    row_nodes = set()

    for n in nodes.values():
        if n.type == "v" and len(n.parents) == 2:
            a, b = n.parents
            if a in value_set:
                row_nodes.add(b)
            elif b in value_set:
                row_nodes.add(a)

    # 2. parent_map 만들기 (t 노드 간)
    parent_map = {}
    for n in nodes.values():
        if n.type != "t":
            continue
        # row parent = t 부모 중 하나
        for p in n.parents:
            if any(p == d or p in nodes for d in row_dims):
                parent_map[n.id] = p
                break

    # 3. 각 row node에 대해 row-dim 값 추출
    rows = []
    for rn in sorted(row_nodes):
        dim_values = {}
        cur = rn
        visited = set()

        while cur and cur not in visited:
            visited.add(cur)
            while cur and cur not in visited:
                visited.add(cur)

                # 이 노드 자체가 row-dim이면 기록
                if cur in row_dims:
                    dim_values[cur] = cur

                # 부모 중 row-dim이면 기록
                for p in nodes[cur].parents:
                    if p in row_dims and p not in dim_values:
                        dim_values[p] = cur

                cur = parent_map.get(cur)
            cur = parent_map.get(cur)

        rows.append((rn, dim_values))

    return rows


# -----------------------------
# Cell values & rowspan
# -----------------------------

def build_cell_map(nodes: Dict[int, Node], value_cols: List[int]) -> Dict[Tuple[int, int], str]:
    """
    (row_leaf_id, value_col_id) -> text
    from v nodes parents=[row_leaf, value_col] (order free)
    """
    value_set = set(value_cols)
    m: Dict[Tuple[int, int], str] = {}
    for n in nodes.values():
        if n.type != "v" or len(n.parents) != 2:
            continue
        a, b = n.parents
        if a in value_set and b not in value_set:
            m[(b, a)] = n.text
        elif b in value_set and a not in value_set:
            m[(a, b)] = n.text
    return m


def compute_rowspans(row_text_rows: List[List[str]]) -> Tuple[Dict[Tuple[int, int], int], Set[Tuple[int, int]]]:
    """
    Hierarchical rowspan for row header columns.
    row_text_rows: rows x row_header_cols values (strings)
    """
    n = len(row_text_rows)
    if n == 0:
        return {}, set()
    c = len(row_text_rows[0])
    rowspan: Dict[Tuple[int, int], int] = {}
    hidden: Set[Tuple[int, int]] = set()

    for col in range(c):
        i = 0
        while i < n:
            v = row_text_rows[i][col]
            if v == "":
                rowspan[(i, col)] = 1
                i += 1
                continue
            span = 1
            for j in range(i + 1, n):
                # boundary: all previous cols equal
                if any(row_text_rows[j][pc] != row_text_rows[i][pc] for pc in range(col)):
                    break
                if row_text_rows[j][col] == v:
                    span += 1
                else:
                    break
            rowspan[(i, col)] = span
            for k in range(i + 1, i + span):
                hidden.add((k, col))
            i += span
    return rowspan, hidden


# -----------------------------
# HTML rendering
# -----------------------------

def render_html_doc(
    title: str,
    row_dim_texts: List[str],
    value_col_texts: List[str],
    row_text_rows: List[List[str]],
    value_rows: List[List[str]],
) -> str:
    esc = html.escape

    # rowspan for row headers
    rowspan_map, hidden_cells = compute_rowspans(row_text_rows)

    out: List[str] = []
    out.append("<table>")
    out.append("<thead><tr>")
    for t in row_dim_texts:
        out.append(f"<th>{esc(t)}</th>")
    for t in value_col_texts:
        out.append(f"<th>{esc(t)}</th>")
    out.append("</tr></thead>")

    out.append("<tbody>")
    for r_idx in range(len(row_text_rows)):
        out.append("<tr>")
        # row header cells with rowspan
        for c_idx, txt in enumerate(row_text_rows[r_idx]):
            if (r_idx, c_idx) in hidden_cells:
                continue
            span = rowspan_map.get((r_idx, c_idx), 1)
            attrs = f' rowspan="{span}"' if span > 1 else ""
            out.append(f"<td{attrs}>{esc(txt)}</td>")
        # value cells
        for val in value_rows[r_idx]:
            out.append(f"<td class='num'>{esc(val)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")

    table_html = "\n".join(out)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>{esc(title)}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      padding: 24px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    th, td {{
      border: 1px solid #444;
      padding: 6px 10px;
      font-size: 14px;
      vertical-align: top;
    }}
    th {{
      background: #f2f2f2;
    }}
    td.num {{
      text-align: right;
      white-space: nowrap;
    }}
  </style>
</head>
<body>
  <h1>{esc(title)}</h1>
  {table_html}
</body>
</html>
""".strip()


# -----------------------------
# Main / CLI
# -----------------------------

def main(input_path: str, output_path: str | None = None) -> int:
    in_path = Path(input_path)
    out_path = Path(
        output_path) if output_path else in_path.with_suffix(".html")

    nodes = parse_mpdx_text(in_path)
    title_node = find_first(nodes, "title")
    table_node = find_first(nodes, "table")

    _table_id, dim_root_parent_id = pick_dimension_root_id(nodes)

    dims = dimension_roots(nodes, dim_root_parent_id)
    if not dims:
        raise ValueError(
            "No dimension roots found. (Expected t children under table or title)")

    row_dims, value_cols = split_row_dims_and_value_cols(nodes, dims)

    if not row_dims:
        raise ValueError(
            "No row dimensions inferred. (All dimensions look like value dims)")

    if not value_cols:
        raise ValueError(
            "No value columns inferred. (No v nodes referencing leaf columns)")

    # Build rows as chains across row-dims
    chains = build_rows(nodes, row_dims, value_cols)

    # Build cell map
    cell_map = build_cell_map(nodes, value_cols)

    # Human-readable header texts
    row_dim_texts = [nodes[d].text for d in row_dims]
    value_col_texts = [nodes[c].text for c in value_cols]

    # Render row header texts & values
    row_text_rows: List[List[str]] = []
    value_rows: List[List[str]] = []

    rows = build_rows(nodes, row_dims, value_cols)

    row_text_rows: List[List[str]] = []
    value_rows: List[List[str]] = []

    for row_leaf, dim_values in rows:
        # row header 값: row_dims 순서대로 채움
        row_texts: List[str] = []
        for d in row_dims:
            v = dim_values.get(d)
            row_texts.append(nodes[v].text if v else "")
        row_text_rows.append(row_texts)

        # value columns
        vals: List[str] = []
        for col in value_cols:
            vals.append(cell_map.get((row_leaf, col), "-"))
        value_rows.append(vals)

    html_doc = render_html_doc(
        title=title_node.text or "MPDX Table",
        row_dim_texts=row_dim_texts,
        value_col_texts=value_col_texts,
        row_text_rows=row_text_rows,
        value_rows=value_rows,
    )

    out_path.write_text(html_doc, encoding="utf-8")
    print(f"✅ Wrote: {out_path}")
    return 0


def cli() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python mdpx_to_html.py <input.mpdx> [output.html]", file=sys.stderr)
        raise SystemExit(2)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) >= 3 else None
    raise SystemExit(main(inp, out))


if __name__ == "__main__":
    cli()
