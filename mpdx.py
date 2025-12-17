from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Iterable
import html
import re


@dataclass(frozen=True)
class Node:
    id: int
    parents: Tuple[int, ...]  # 0 means root
    type: str
    text: str


def _parse_parents(raw: str) -> Tuple[int, ...]:
    raw = (raw or "").strip()
    if raw == "":
        return tuple()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return tuple()
        parts = [p.strip() for p in inner.split(",")]
        return tuple(int(p) for p in parts if p != "")
    return (int(raw),)


def parse_content_tsv(content_tsv: str) -> Dict[int, Node]:
    """
    Accepts TSV with header:
      id<TAB>parents<TAB>type<TAB>text
    """
    lines = [ln for ln in content_tsv.splitlines() if ln.strip()]
    if not lines:
        raise ValueError("Empty content")

    header = [h.strip().lower() for h in re.split(r"\t+", lines[0].strip())]
    # expected columns
    try:
        id_i = header.index("id")
        parents_i = header.index("parents")
        type_i = header.index("type")
        text_i = header.index("text")
    except ValueError as e:
        raise ValueError(f"Bad header. Expected columns: id, parents, type, text. Got: {header}") from e

    nodes: Dict[int, Node] = {}
    for ln in lines[1:]:
        cols = re.split(r"\t+", ln.rstrip("\n"))
        # pad if missing
        while len(cols) <= max(id_i, parents_i, type_i, text_i):
            cols.append("")
        nid = int(cols[id_i].strip())
        parents = _parse_parents(cols[parents_i])
        ntype = cols[type_i].strip()
        ntext = cols[text_i] if text_i < len(cols) else ""
        ntext = (ntext or "").strip()
        nodes[nid] = Node(id=nid, parents=parents, type=ntype, text=ntext)
    return nodes


def _children_index(nodes: Dict[int, Node]) -> Dict[int, List[int]]:
    """Only single-parent edges contribute to the containment tree."""
    ch: Dict[int, List[int]] = {}
    for n in nodes.values():
        if len(n.parents) == 1:
            p = n.parents[0]
            ch.setdefault(p, []).append(n.id)
    # stable order by id (you can change to custom ordering later)
    for k in ch:
        ch[k].sort()
    return ch


def _descendants(ch: Dict[int, List[int]], root: int) -> List[int]:
    out: List[int] = []
    stack = [root]
    while stack:
        cur = stack.pop()
        for c in ch.get(cur, []):
            out.append(c)
            stack.append(c)
    return out


def _find_first_list_under_title(nodes: Dict[int, Node], ch: Dict[int, List[int]], title_id: int) -> Optional[int]:
    for cid in ch.get(title_id, []):
        if nodes[cid].type == "list":
            return cid
    return None


def _collect_column_nodes(nodes: Dict[int, Node], ch: Dict[int, List[int]], col_list_id: int) -> List[int]:
    # columns are "t" nodes directly under the list
    cols = [cid for cid in ch.get(col_list_id, []) if nodes[cid].type in ("t", "title")]
    return cols


def _infer_row_roots(nodes: Dict[int, Node], ch: Dict[int, List[int]], title_id: int, col_list_id: int) -> List[int]:
    """
    Heuristic:
    - Everything under title except the column list is treated as row-region roots.
    """
    roots: List[int] = []
    for cid in ch.get(title_id, []):
        if cid == col_list_id:
            continue
        roots.append(cid)
    return roots


def _iter_row_items(nodes: Dict[int, Node], ch: Dict[int, List[int]], root_ids: Iterable[int]) -> List[Tuple[int, int]]:
    """
    Returns list of (node_id, depth) for row-like items.
    We consider nodes of type 't' as displayable row labels,
    and keep hierarchical depth based on single-parent tree.
    """
    items: List[Tuple[int, int]] = []

    def dfs(nid: int, depth: int) -> None:
        n = nodes[nid]
        # show label rows for t / title / list-as-group if it has text
        if n.type in ("t", "title") and n.text:
            items.append((nid, depth))
        elif n.type == "list":
            # group node itself isn't a label unless it has text (often empty)
            if n.text:
                items.append((nid, depth))

        for cid in ch.get(nid, []):
            dfs(cid, depth + (1 if n.type == "list" else 0))

    for rid in root_ids:
        dfs(rid, 0)
    return items


def _value_map(nodes: Dict[int, Node]) -> Dict[Tuple[int, int], str]:
    """
    Map (row_node_id, col_node_id) -> value text from v nodes with parents [col, row] or [row, col].
    """
    m: Dict[Tuple[int, int], str] = {}
    for n in nodes.values():
        if n.type != "v":
            continue
        if len(n.parents) != 2:
            continue
        a, b = n.parents
        # store both orientations; later lookup will succeed regardless of ordering
        m[(a, b)] = n.text
        m[(b, a)] = n.text
    return m


def mpdx_content_to_html_table(
    content_tsv: str,
    *,
    title_id: int = 2,
    empty_cell: str = "-",
    first_col_header: str = "항목",
) -> str:
    """
    Convert MPDX content.txt TSV into an HTML table.

    Assumptions/heuristics:
    - title node id defaults to 2 (as in your examples)
    - the first 'list' under title defines the column headers (t nodes)
    - remaining children under title define the row region (hierarchical)
    - v nodes link (row, col) by multi-parents
    """
    nodes = parse_content_tsv(content_tsv)
    ch = _children_index(nodes)

    if title_id not in nodes:
        raise ValueError(f"title_id={title_id} not found in nodes")

    col_list_id = _find_first_list_under_title(nodes, ch, title_id)
    if col_list_id is None:
        raise ValueError("Could not find a column list under title node")

    col_node_ids = _collect_column_nodes(nodes, ch, col_list_id)
    if not col_node_ids:
        raise ValueError("No column nodes found under the column list")

    row_roots = _infer_row_roots(nodes, ch, title_id, col_list_id)
    row_items = _iter_row_items(nodes, ch, row_roots)

    vmap = _value_map(nodes)

    def esc(s: str) -> str:
        return html.escape(s, quote=True)

    # Build HTML
    out: List[str] = []
    out.append('<table border="1" cellspacing="0" cellpadding="6">')

    # Header
    out.append("<thead><tr>")
    out.append(f"<th>{esc(first_col_header)}</th>")
    for cid in col_node_ids:
        out.append(f"<th>{esc(nodes[cid].text)}</th>")
    out.append("</tr></thead>")

    # Body
    out.append("<tbody>")
    for rid, depth in row_items:
        label = nodes[rid].text
        indent = "&nbsp;" * (depth * 4)
        out.append("<tr>")
        out.append(f"<td>{indent}{esc(label)}</td>")

        for cid in col_node_ids:
            val = vmap.get((rid, cid), "")
            if val == "":
                val = empty_cell
            out.append(f"<td>{esc(val)}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")

    return "\n".join(out)


if __name__ == "__main__":
    sample = """id\tparents\ttype\ttext
1\t0\ttable\t
2\t1\ttitle\t예산
3\t2\tlist\t
4\t3\tt\t계획 금액
5\t3\tt\t집행액
6\t3\tt\t잔액
7\t3\tt\t비고
10\t2\tlist\t
11\t10\tt\t직접비 소계
12\t[11,4]\tv\t41000000
13\t[11,5]\tv\t41000000
"""
    html_table = mpdx_content_to_html_table(sample, title_id=2)
    print(html_table)
