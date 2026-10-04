# MPDX — Multi-Parent Document Exchange

> **A report has one most concise, most beautiful form. What a person writes is the content;
> the form belongs to the system.**

MPDX stores a document's **content with its formatting removed**. Written as `md+mpdx` — Markdown
for prose, MPDX for tables — a document can be **reproduced** from that file alone: the editor
applies its forms and lays the tables out again. The tables may come back arranged differently
(split, merged, transposed); what the document chose to emphasize may change. **The content does
not.** Two documents with the same md+mpdx are the same document.

> 보고서에는 가장 간결하고 아름다운 하나의 형식이 있다. md+mpdx 는 문서의 서식을 제거한 채
> 내용만 그대로 저장하고, 이것만으로 문서를 다시 재현할 수 있다. 표의 구성이나 표현은 달라질 수
> 있지만 문서의 내용은 같다.

**Latest specification: [`spec/mpdx-v2.1.md`](spec/mpdx-v2.1.md)** — home: https://gitoky.com/bckim/mpdx

---

## The idea in one table

A value is not "row 3, column 2". It is the value of something:

```
1	0	tbl	Table 3 3
2:4	1	t	Item|Planned|Used
5	1	t	Labor
6	1	t	Materials
7:8	[5,3:]	t	20,000|18,000      ← Labor × Planned, Labor × Used
9:10	[6,3:]	t	5,000|4,200
```

Each node lists its parents. A value is the intersection of its parents' meanings, and parent
order means nothing. Whether *Labor* becomes a row header and *Planned* a column header — or the
other way round — is a rendering decision.

## Stacks

Several tables with the same labels and different values (a budget per institution) are written
once, with the extra dimension as an axis:

```
52	1	ax	구분
53:55	52	t	주관|공동 A|공동 B
200:203	[44,4:,53]	t	98,000|97,000||       ← row 44, columns 4…7, layer 53
```

See [`examples/`](examples/): the same document as one stacked block (125 lines) and as three
separate tables (249 lines).

## md+mpdx

~~~markdown
# 1. 사업 개요

본 사업은 …

□ 예산사용현황

```mpdx
# MPDX v2.1 — 22행 10열, 헤더 1행
# spec: https://gitoky.com/bckim/mpdx (spec/mpdx-v2.1.md)
…
```
~~~

Simple tables stay GitHub-flavored pipe tables; tables with merged cells become `mpdx` blocks.
Every MPDX block names its version and points to its spec.

## Versions

| Version | Date | Where |
|---|---|---|
| v0.1 | 2025-12 | github.com/husky81/mpdx — the model (semantic graph, multi-parent values) |
| v2.0 | 2026-08 | CellDocs internal |
| **v2.1** | 2026-10-04 | **https://gitoky.com/bckim/mpdx** — first public serialization |

From v2.1 on, MPDX is maintained at **https://gitoky.com/bckim/mpdx** only. The GitHub repository
keeps this v2.1 snapshot and is not updated further.

## Implementations

- **CellDocs** (celldocs.kr) — writes md+mpdx (`MPDX 내보내기`), reads and patches MPDX tables
  through its MCP tools (`read_table`, `update_table_cells`, including stacks). Importing an
  md+mpdx file back into a document (reproduction without the original, §4 of the spec) is in
  progress.
- **`src/`** — the v0.1 experimental Python tooling (HTML ↔ MPDX). It predates v2.1 and does not
  read stacks or compaction.

```python
import mpdx                          # v0.1 tooling
mp = mpdx.from_html("a.html")
for n in mp.find(type="t"):
    print(n.text)
html = mp.to_html()
```

## License

MIT — see [`LICENSE`](LICENSE).
