#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mdpx_to_html.py  (MPDX → HTML)

Reads a text-form MPDX (your comment-friendly TSV) and writes an HTML file.
Supports:
- Comment lines starting with '#'
- parents as '0', '12', or '[12, 34]'
- "list-less" MPDX encoding where hierarchy is expressed via multi-parents:
    - One parent is the column id (e.g., 세목)
    - Another parent is the logical row parent (e.g., 직접비)

Heuristics (designed to avoid "Sudoku"):
- The first node with type=title is the table title.
- Top-level columns are t-nodes whose parent is the title id.
- Column hierarchy comes from t-nodes whose parent is another column node.
- Leaf columns are used as value columns unless they look like row-headers.
- Row-headers are leaf columns that have t-nodes attached but no v-nodes attached
  (plus special-case: "비고" treated as value column).
- Rows are generated from the row hierarchy inferred from multi-parents:
    row_parent(row_node) = any parent that is not a column id
- A row is "materialized" if it has any value cell (v or note-text).
- Rowspan is auto-calculated for row-header columns.

Usage:
  python mdpx_to_html.py money_plan.mpdx money_plan.html
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Iterable
import html
import re
import sys


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
        line = line.rstrip("\n")
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        cols = re.split(r"\t+", line.strip())
        if len(cols) < 3:
            continue
        # 2️⃣ 헤더 라인 자동 무시
        if not cols[0].isdigit():
            continue
        nid = int(cols[0].strip())
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


def find_title(nodes: Dict[int, Node]) -> Node:
    titles = [n for n in nodes.values() if n.type == "title"]
    if not titles:
        raise ValueError("No title node found (type=title).")
    return sorted(titles, key=lambda n: n.id)[0]


def collect_column_nodes(nodes: Dict[int, Node], title_id: int) -> Set[int]:
    # Column nodes are t nodes reachable from title via parent chain among column nodes.
    col_ids: Set[int] = set()
    # seed: t nodes whose parent is title_id
    frontier = [n.id for n in nodes.values() if n.type ==
                "t" and title_id in n.parents]
    col_ids.update(frontier)
    # expand: any t node whose parent includes a column id (single-parent columns)
    changed = True
    while changed:
        changed = False
        for n in nodes.values():
            if n.type != "t":
                continue
            if n.id in col_ids:
                continue
            # If any parent is an already-known column node, treat as column child
            if any(p in col_ids for p in n.parents):
                col_ids.add(n.id)
                changed = True
    return col_ids


def column_children(nodes: Dict[int, Node], col_ids: Set[int]) -> Dict[int, List[int]]:
    """
    For columns, treat parent->child relation when child has exactly one parent that is a column id.
    If multiple parents include column ids, we ignore (ambiguous for column tree).
    """
    ch: Dict[int, List[int]] = {}
    for n in nodes.values():
        if n.id not in col_ids:
            continue
        col_parents = [p for p in n.parents if p in col_ids]
        if len(col_parents) == 1:
            ch.setdefault(col_parents[0], []).append(n.id)
    for k in ch:
        ch[k].sort()
    return ch


def leaf_columns(col_ids: Set[int], col_ch: Dict[int, List[int]]) -> List[int]:
    non_leaf = set(col_ch.keys())
    for kids in col_ch.values():
        non_leaf.update(kids)
    # leaf = in col_ids but not a parent of any other col node
    parents_with_children = set(col_ch.keys())
    leaves = [cid for cid in col_ids if cid not in parents_with_children]
    return sorted(leaves)


def classify_columns(
    nodes: Dict[int, Node],
    title_id: int,
    col_ids: Set[int],
    col_ch: Dict[int, List[int]],
) -> Tuple[List[int], List[int], List[List[int]]]:
    """
    Returns:
      row_header_cols: ordered list of column ids to appear on the left (merged by rowspan)
      value_cols: ordered list of leaf column ids to appear as data columns (right side)
      header_rows: column header rows for HTML (each row is list of col ids or groups)
                  For simplicity we return a 2-level header if needed.
    """
    # Top-level columns: parents include title_id (direct columns)
    top_cols = sorted(
        [cid for cid in col_ids if title_id in nodes[cid].parents])

    # Identify which leaf columns have v-values attached
    v_nodes = [n for n in nodes.values() if n.type ==
               "v" and len(n.parents) == 2]
    leaf_set = set(leaf_columns(col_ids, col_ch))
    has_v: Set[int] = set()
    for v in v_nodes:
        a, b = v.parents
        if a in leaf_set:
            has_v.add(a)
        if b in leaf_set:
            has_v.add(b)

    # Identify which leaf columns have t-values attached (like 비고 text)
    leaf_has_attached_t: Set[int] = set()
    for n in nodes.values():
        if n.type != "t" or n.id in col_ids:
            continue
        for p in n.parents:
            if p in leaf_set:
                leaf_has_attached_t.add(p)

    # Heuristic for row headers:
    # - must be a top-level leaf column
    # - has attached t nodes (row items)
    # - does NOT have v nodes attached
    # - except "비고" should be treated as value column
    def is_note_col(cid: int) -> bool:
        txt = (nodes[cid].text or "").strip().lower()
        return txt in {"비고", "remark", "note", "notes", "memo", "메모"}

    row_header_cols: List[int] = []
    value_cols: List[int] = []

    # Determine leaf columns order: left-to-right by walking top-level columns.
    def collect_leafs_under(col_id: int) -> List[int]:
        # DFS column tree to gather leafs
        out: List[int] = []
        stack = [col_id]
        while stack:
            cur = stack.pop()
            kids = col_ch.get(cur, [])
            if not kids:
                if cur in leaf_set:
                    out.append(cur)
            else:
                for k in reversed(kids):
                    stack.append(k)
        return out

    ordered_leafs: List[int] = []
    for tc in top_cols:
        ordered_leafs.extend(collect_leafs_under(tc))

    for cid in top_cols:
        if cid in leaf_set:
            # top-level leaf column
            if (cid in leaf_has_attached_t) and (cid not in has_v) and (not is_note_col(cid)):
                row_header_cols.append(cid)

    for lc in ordered_leafs:
        if lc in row_header_cols:
            continue
        value_cols.append(lc)

    # Build header rows:
    # If any top_col has children, use 2 header rows: top group + leaves
    any_group = any(col_ch.get(tc) for tc in top_cols)
    header_rows: List[List[int]] = []
    if any_group:
        # Row 1: top-level columns (some with colspan)
        header_rows.append(top_cols)
        # Row 2: leaf columns in ordered_leafs but aligned by top groups
        header_rows.append(ordered_leafs)
    else:
        header_rows.append(ordered_leafs)

    return row_header_cols, value_cols, header_rows


def infer_row_parent(
    node: Node,
    col_ids: Set[int],
) -> Optional[int]:
    """
    For a row node (t not in col_ids), infer its logical parent row node:
      choose any parent that is not a column id and not 0.
    If none, return None.
    """
    for p in node.parents:
        if p == 0:
            continue
        if p in col_ids:
            continue
        return p
    return None


def row_column_of_node(node: Node, col_ids: Set[int]) -> Optional[int]:
    """If a row node is attached to a specific column, return that column id."""
    for p in node.parents:
        if p in col_ids:
            return p
    return None


def build_row_tree(
    nodes: Dict[int, Node],
    col_ids: Set[int],
) -> Tuple[Dict[int, Optional[int]], Dict[Optional[int], List[int]]]:
    """
    Returns:
      parent_map[row_node_id] = parent_row_node_id or None
      children_map[parent_row_node_id or None] = list of child row_node_ids
    """
    parent_map: Dict[int, Optional[int]] = {}
    children_map: Dict[Optional[int], List[int]] = {}

    for n in nodes.values():
        if n.type != "t":
            continue
        if n.id in col_ids:
            continue
        p = infer_row_parent(n, col_ids)
        parent_map[n.id] = p
        children_map.setdefault(p, []).append(n.id)

    for k in children_map:
        children_map[k].sort()

    return parent_map, children_map


def build_value_maps(
    nodes: Dict[int, Node],
    value_cols: List[int],
    col_ids: Set[int],
) -> Tuple[Dict[Tuple[int, int], str], Dict[Tuple[int, int], str]]:
    """
    Returns:
      vmap[(row_node_id, value_col_id)] = value text  (from v nodes)
      tmap[(row_node_id, value_col_id)] = value text  (from t nodes attached to value col, e.g. notes)
    """
    value_col_set = set(value_cols)
    vmap: Dict[Tuple[int, int], str] = {}
    tmap: Dict[Tuple[int, int], str] = {}

    for n in nodes.values():
        if n.type == "v" and len(n.parents) == 2:
            a, b = n.parents
            if a in value_col_set and b not in col_ids:
                vmap[(b, a)] = n.text
            elif b in value_col_set and a not in col_ids:
                vmap[(a, b)] = n.text

    for n in nodes.values():
        if n.type != "t" or n.id in col_ids:
            continue
        # if attached to a value col and a row-parent
        col_parent = None
        row_parent = None
        for p in n.parents:
            if p in value_col_set:
                col_parent = p
            elif p != 0 and p not in col_ids:
                row_parent = p
        if col_parent is not None and row_parent is not None and n.text:
            tmap[(row_parent, col_parent)] = n.text

    return vmap, tmap


def materialize_rows(
    nodes: Dict[int, Node],
    title_id: int,
    row_header_cols: List[int],
    value_cols: List[int],
    col_ids: Set[int],
) -> List[Dict[int, Optional[str]]]:
    """
    Produce a list of row dicts:
      row[col_id] = display string (for header cols) or cell value (for value cols)
    Each row corresponds to a row-node that has any value attached (directly or in descendants).
    """
    parent_map, children_map = build_row_tree(nodes, col_ids)
    vmap, tmap = build_value_maps(nodes, value_cols, col_ids)

    # Determine which row nodes "carry data" (have any value) either directly or via descendants.
    data_nodes: Set[int] = set()
    for (rid, _cid) in vmap.keys():
        data_nodes.add(rid)
    for (rid, _cid) in tmap.keys():
        data_nodes.add(rid)

    # propagate: any ancestor of a data node should be kept as possible row context,
    # but we will materialize rows at the data node itself (leaf-ish) for clarity.
    def ancestors(nid: int) -> List[int]:
        out = []
        cur = nid
        while True:
            p = parent_map.get(cur)
            if p is None:
                break
            out.append(p)
            cur = p
        return out

    keep_nodes: Set[int] = set(data_nodes)
    for dn in list(data_nodes):
        keep_nodes.update(ancestors(dn))

    # Sort rows by tree traversal from roots, but only output rows for data_nodes (in traversal order).
    # Root candidates: nodes whose parent_map is None AND belong to the first row header column.
    first_row_col = row_header_cols[0] if row_header_cols else None

    def belongs_to_col(nid: int, col_id: int) -> bool:
        n = nodes[nid]
        return any(p == col_id for p in n.parents)

    roots = [nid for nid, p in parent_map.items() if p is None and (
        first_row_col is None or belongs_to_col(nid, first_row_col))]
    roots.sort()

    ordered: List[int] = []

    def dfs(nid: int):
        if nid in keep_nodes:
            ordered.append(nid)
        for c in children_map.get(nid, []):
            dfs(c)

    for r in roots:
        dfs(r)

    # Build per-row header display for each materialized row node.
    # For each header col, find:
    #  - for first header col: nearest ancestor (including self) that belongs to that col
    #  - for later header cols: deepest in chain that belongs to that col (often the current node)
    def chain(nid: int) -> List[int]:
        # from root to nid
        up = [nid]
        cur = nid
        while True:
            p = parent_map.get(cur)
            if p is None:
                break
            up.append(p)
            cur = p
        return list(reversed(up))

    rows: List[Dict[int, Optional[str]]] = []
    for rid in ordered:
        # Only materialize if it has data directly OR has no children in keep_nodes and has data in subtree
        # Practical: materialize when it has direct v/t values, or when it's a leaf in keep_nodes.
        has_direct = any(k[0] == rid for k in vmap.keys()) or any(
            k[0] == rid for k in tmap.keys())
        if not has_direct:
            # materialize if no kept children
            kept_children = [c for c in children_map.get(
                rid, []) if c in keep_nodes]
            if kept_children:
                continue

        row: Dict[int, Optional[str]] = {}
        chn = chain(rid)

        # header columns
        for idx, col in enumerate(row_header_cols):
            candidates = [n for n in chn if any(
                p == col for p in nodes[n].parents)]
            if not candidates:
                row[col] = ""
                continue
            if idx == 0:
                chosen = candidates[0]  # nearest from top
            else:
                chosen = candidates[-1]  # deepest
            row[col] = nodes[chosen].text

        # value columns: find value at rid, else walk ancestors up
        def lookup_value(row_node: int, col_id: int) -> Optional[str]:
            cur = row_node
            while True:
                if (cur, col_id) in vmap:
                    return vmap[(cur, col_id)]
                if (cur, col_id) in tmap:
                    return tmap[(cur, col_id)]
                p = parent_map.get(cur)
                if p is None:
                    return None
                cur = p

        for col in value_cols:
            val = lookup_value(rid, col)
            row[col] = val if val is not None else "-"
        # store internal id for potential debugging
        row[-1] = str(rid)

        rows.append(row)

    return rows


def compute_rowspans(rows: List[Dict[int, Optional[str]]], merge_cols: List[int]) -> Tuple[Dict[Tuple[int, int], int], Set[Tuple[int, int]]]:
    """
    Hierarchical rowspan computation:
    - Merge identical consecutive values in a column
    - But only within boundaries where all previous merge_cols are identical
    """
    rowspan: Dict[Tuple[int, int], int] = {}
    hidden: Set[Tuple[int, int]] = set()
    n = len(rows)

    for col_idx, col in enumerate(merge_cols):
        i = 0
        while i < n:
            v = rows[i].get(col, "")
            if v in (None, ""):
                rowspan[(i, col)] = 1
                i += 1
                continue

            span = 1
            for j in range(i + 1, n):
                # boundary check for parent cols
                boundary_ok = True
                for parent_col in merge_cols[:col_idx]:
                    if rows[j].get(parent_col, "") != rows[i].get(parent_col, ""):
                        boundary_ok = False
                        break
                if not boundary_ok:
                    break
                if rows[j].get(col, "") == v:
                    span += 1
                else:
                    break

            rowspan[(i, col)] = span
            for k in range(i + 1, i + span):
                hidden.add((k, col))
            i += span

    return rowspan, hidden


def render_html(
    title: str,
    header_rows: List[List[int]],
    row_header_cols: List[int],
    value_cols: List[int],
    columns_text: Dict[int, str],
    rows: List[Dict[int, Optional[str]]],
) -> str:
    esc = html.escape

    # For 2-level headers, compute colspans for top row.
    colspans: Dict[int, int] = {}
    if len(header_rows) == 2:
        top = header_rows[0]
        leaves = header_rows[1]
        # map top col -> count leaves under it by scanning column text ancestry isn't provided here,
        # so assume the leaf list is already ordered and top list partitions it by their appearance:
        # We'll approximate by distributing leaves to the nearest preceding top col.
        # Better: caller can pass explicit mapping; for now, derive from text nesting isn't possible.
        # Practical workaround: if top col is a row_header col or '비고' style, colspan=1.
        # If a top col is not a leaf in leaves, give it the number of leaf columns that are not row_headers and not note?
        # We'll instead compute: if top col appears in leaves => colspan=1 else colspan = number of leaves that are not row headers AND not in top that appear after it until next top.
        leaf_set = set(leaves)
        # build positions
        leaf_pos = {c: i for i, c in enumerate(leaves)}
        # naive: if top in leaf_set -> 1 else -> count of leaf columns whose text is not empty and not in row_header_cols and between segments by position order
        # Use a simple split based on order in leaves: assume each non-leaf top owns the next K leaves until next top that is also a leaf.
        # We'll do: scan leaves, assign owner as last seen top that is not a leaf.
        owners: Dict[int, List[int]] = {t: [] for t in top}
        current_owner: Optional[int] = None
        for leaf in leaves:
            if leaf in top and leaf in leaf_set:
                current_owner = None  # reset; it's standalone
                owners[leaf].append(leaf)
            else:
                # assign to last top that is not itself a leaf and has been seen in top
                if current_owner is None:
                    # choose the first non-leaf top
                    non_leaf_tops = [t for t in top if t not in leaf_set]
                    current_owner = non_leaf_tops[0] if non_leaf_tops else top[0]
                owners[current_owner].append(leaf)
        for t in top:
            colspans[t] = max(1, len(owners.get(t, [])))
    # Rowspan for row-header cols
    rowspan_map, hidden_cells = compute_rowspans(rows, row_header_cols)

    # Build ordered leaf display columns: left = row headers, right = value cols
    display_cols = row_header_cols + value_cols

    out: List[str] = []
    out.append("<table>")
    out.append("<thead>")
    if len(header_rows) == 2:
        # Row 1
        out.append("<tr>")
        for cid in header_rows[0]:
            txt = columns_text.get(cid, "")
            span = colspans.get(cid, 1)
            if span > 1:
                out.append(f"<th colspan=\"{span}\">{esc(txt)}</th>")
            else:
                out.append(f"<th>{esc(txt)}</th>")
        out.append("</tr>")
        # Row 2: only leaf headers in display order
        out.append("<tr>")
        for cid in display_cols:
            out.append(f"<th>{esc(columns_text.get(cid, ''))}</th>")
        out.append("</tr>")
    else:
        out.append("<tr>")
        for cid in display_cols:
            out.append(f"<th>{esc(columns_text.get(cid, ''))}</th>")
        out.append("</tr>")
    out.append("</thead>")

    out.append("<tbody>")
    for r_idx, row in enumerate(rows):
        out.append("<tr>")
        for cid in display_cols:
            if (r_idx, cid) in hidden_cells:
                continue
            cell = row.get(cid, "")
            span = rowspan_map.get((r_idx, cid), 1)
            attrs = f' rowspan="{span}"' if (
                cid in row_header_cols and span > 1) else ""
            out.append(
                f"<td{attrs}>{esc(str(cell) if cell is not None else '')}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")

    table_html = "\n".join(out)

    doc = f"""<!DOCTYPE html>
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
    td:nth-child(n+{len(row_header_cols)+1}) {{
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
"""
    return doc


def main(input_path: str, output_path: str | None = None) -> int:
    in_path = Path(input_path)

    if output_path:
        out_path = Path(output_path)
    else:
        out_path = in_path.with_suffix(".html")

    nodes = parse_mpdx_text(in_path)
    title = find_title(nodes)
    title_id = title.id

    col_ids = collect_column_nodes(nodes, title_id)
    col_ch = column_children(nodes, col_ids)
    row_header_cols, value_cols, header_rows = classify_columns(
        nodes, title_id, col_ids, col_ch)

    # Build column text map for headers
    columns_text = {cid: nodes[cid].text for cid in col_ids}
    # Ensure displayed columns have text
    for cid in (row_header_cols + value_cols):
        columns_text.setdefault(cid, nodes.get(
            cid, Node(cid, tuple(), "t", "")).text if cid in nodes else "")

    rows = materialize_rows(
        nodes, title_id, row_header_cols, value_cols, col_ids)

    html_doc = render_html(
        title=title.text or "MPDX Table",
        header_rows=header_rows,
        row_header_cols=row_header_cols,
        value_cols=value_cols,
        columns_text=columns_text,
        rows=rows,
    )
    out_path.write_text(html_doc, encoding="utf-8")
    print(f"✅ Wrote: {out_path}")
    return 0


def cli():
    if len(sys.argv) < 2:
        print(
            "Usage: python mdpx_to_html.py <input.mpdx> [output.html]",
            file=sys.stderr,
        )
        raise SystemExit(2)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else None
    raise SystemExit(main(input_path, output_path))


if __name__ == "__main__":
    cli()