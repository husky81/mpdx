from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List
import html
import re
from pathlib import Path


# ---------- Data Model ----------

@dataclass(frozen=True)
class Node:
    id: int
    parents: Tuple[int, ...]
    type: str
    text: str


# ---------- Parsing ----------

def _parse_parents(raw: str) -> Tuple[int, ...]:
    raw = (raw or "").strip()
    if not raw:
        return tuple()
    if raw.startswith("["):
        return tuple(int(x.strip()) for x in raw[1:-1].split(","))
    return (int(raw),)


def parse_content_tsv(tsv: str) -> Dict[int, Node]:
    lines = [l for l in tsv.splitlines() if l.strip()]
    header = re.split(r"\t+", lines[0])
    idx = {h: i for i, h in enumerate(header)}

    nodes: Dict[int, Node] = {}
    for line in lines[1:]:
        cols = re.split(r"\t+", line)
        nid = int(cols[idx["id"]])
        parents = _parse_parents(cols[idx["parents"]])
        ntype = cols[idx["type"]]
        text = cols[idx["text"]] if idx["text"] < len(cols) else ""
        nodes[nid] = Node(nid, parents, ntype, text.strip())
    return nodes


# ---------- HTML Rendering ----------

def mpdx_to_html_table(
    content_tsv: str,
    *,
    title_id: int = 2,
    empty_cell: str = "-"
) -> str:
    nodes = parse_content_tsv(content_tsv)

    # column headers = first list under title
    children = {}
    for n in nodes.values():
        if len(n.parents) == 1:
            children.setdefault(n.parents[0], []).append(n.id)

    col_list = next(
        nid for nid in children.get(title_id, [])
        if nodes[nid].type == "list"
    )
    col_ids = [cid for cid in children[col_list] if nodes[cid].type == "t"]

    # row roots = other children under title
    row_roots = [cid for cid in children[title_id] if cid != col_list]

    # flatten rows
    rows: List[int] = []

    def walk(nid: int):
        if nodes[nid].type == "t" and nodes[nid].text:
            rows.append(nid)
        for c in children.get(nid, []):
            walk(c)

    for r in row_roots:
        walk(r)

    # value map
    values = {}
    for n in nodes.values():
        if n.type == "v" and len(n.parents) == 2:
            a, b = n.parents
            values[(a, b)] = n.text
            values[(b, a)] = n.text

    esc = html.escape
    out = ["<table>"]

    # header
    out.append("<thead><tr><th>항목</th>")
    for cid in col_ids:
        out.append(f"<th>{esc(nodes[cid].text)}</th>")
    out.append("</tr></thead>")

    # body
    out.append("<tbody>")
    for rid in rows:
        out.append("<tr>")
        out.append(f"<td>{esc(nodes[rid].text)}</td>")
        for cid in col_ids:
            out.append(f"<td>{esc(values.get((rid, cid), empty_cell))}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")

    return "\n".join(out)


# ---------- HTML File Writer ----------

def write_html_file(
    table_html: str,
    *,
    title: str = "MPDX Rendered Table",
    output_path: str | Path = "output.html"
) -> None:
    html_doc = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
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
      border: 1px solid #333;
      padding: 6px 10px;
      text-align: left;
      font-size: 14px;
    }}
    th {{
      background: #f2f2f2;
    }}
  </style>
</head>
<body>
<h1>{html.escape(title)}</h1>
{table_html}
</body>
</html>
"""
    Path(output_path).write_text(html_doc, encoding="utf-8")


# ---------- Example Usage ----------

if __name__ == "__main__":
    content = """id\tparents\ttype\ttext
1\t0\ttable\t
2\t1\ttitle\t예산
3\t2\tlist\t
4\t3\tt\t계획 금액
5\t3\tt\t집행액
6\t3\tt\t잔액
10\t2\tlist\t
11\t10\tt\t직접비 소계
12\t[11,4]\tv\t41000000
13\t[11,5]\tv\t41000000
"""

    table_html = mpdx_to_html_table(content)
    write_html_file(
        table_html,
        title="예산 집행 표",
        output_path="budget.html"
    )

    print("✅ budget.html 생성 완료")
