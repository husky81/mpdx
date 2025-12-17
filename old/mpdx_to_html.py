from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List
from pathlib import Path
import html
import re


# -----------------------------
# Data model
# -----------------------------

@dataclass(frozen=True)
class Node:
    id: int
    parents: Tuple[int, ...]
    type: str
    text: str


# -----------------------------
# Parsing helpers
# -----------------------------

def parse_parents(raw: str) -> Tuple[int, ...]:
    raw = raw.strip()
    if not raw or raw == "0":
        return (0,)
    if raw.startswith("["):
        return tuple(int(x.strip()) for x in raw[1:-1].split(","))
    return (int(raw),)


def parse_mpdx_file(path: Path) -> Dict[int, Node]:
    """
    Parses mpdx-like content file:
    - ignores comments (# ...)
    - ignores empty lines
    """
    nodes: Dict[int, Node] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        cols = re.split(r"\t+", line)
        if len(cols) < 3:
            continue

        nid = int(cols[0])
        parents = parse_parents(cols[1])
        ntype = cols[2].strip()
        text = cols[3].strip() if len(cols) > 3 else ""

        nodes[nid] = Node(
            id=nid,
            parents=parents,
            type=ntype,
            text=text
        )

    return nodes


# -----------------------------
# HTML rendering
# -----------------------------

def mpdx_to_html(nodes: Dict[int, Node]) -> str:
    esc = html.escape

    # build single-parent child index
    children: Dict[int, List[int]] = {}
    for n in nodes.values():
        if len(n.parents) == 1:
            p = n.parents[0]
            children.setdefault(p, []).append(n.id)

    for v in children.values():
        v.sort()

    # find title
    title_node = next(n for n in nodes.values() if n.type == "title")
    title_id = title_node.id

    # find column list (first list under title)
    col_list_id = next(
        cid for cid in children.get(title_id, [])
        if nodes[cid].type == "list"
    )

    col_ids = [
        cid for cid in children.get(col_list_id, [])
        if nodes[cid].type == "t"
    ]

    # row roots = other children under title
    row_roots = [
        cid for cid in children.get(title_id, [])
        if cid != col_list_id
    ]

    # flatten row tree
    rows: List[Tuple[int, int]] = []

    def walk(nid: int, depth: int):
        node = nodes[nid]
        if node.type == "t" and node.text:
            rows.append((nid, depth))
        for c in children.get(nid, []):
            walk(c, depth + 1)

    for r in row_roots:
        walk(r, 0)

    # build value map (row, col) -> value
    values: Dict[Tuple[int, int], str] = {}
    for n in nodes.values():
        if n.type == "v" and len(n.parents) == 2:
            a, b = n.parents
            values[(a, b)] = n.text
            values[(b, a)] = n.text

    # render HTML
    out: List[str] = []
    out.append("<table>")
    out.append("<thead>")
    out.append("<tr>")
    out.append("<th>항목</th>")
    for cid in col_ids:
        out.append(f"<th>{esc(nodes[cid].text)}</th>")
    out.append("</tr>")
    out.append("</thead>")
    out.append("<tbody>")

    for rid, depth in rows:
        label = "&nbsp;" * (depth * 4) + esc(nodes[rid].text)
        out.append("<tr>")
        out.append(f"<td>{label}</td>")
        for cid in col_ids:
            out.append(
                f"<td>{esc(values.get((rid, cid), '-'))}</td>"
            )
        out.append("</tr>")

    out.append("</tbody></table>")

    return f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{esc(title_node.text)}</title>
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
}}
th {{
  background: #f0f0f0;
}}
</style>
</head>
<body>
<h1>{esc(title_node.text)}</h1>
{''.join(out)}
</body>
</html>
""".strip()


# -----------------------------
# Entry point
# -----------------------------

if __name__ == "__main__":
    mpdx_path = Path("mpdx_samples\money_plan.mpdx")
    html_path = Path("money_plan.html")

    nodes = parse_mpdx_file(mpdx_path)
    html_doc = mpdx_to_html(nodes)

    html_path.write_text(html_doc, encoding="utf-8")
    print(f"✅ HTML 파일 생성 완료: {html_path}")
