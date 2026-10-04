# MPDX Specification — v2.1

**MPDX — Multi-Parent Document Exchange**
Version: v2.1
Status: Working draft — the serialization CellDocs emits today
Last updated: 2026-10-04
Home: https://gitoky.com/bckim/mpdx (every version stays at `spec/mpdx-v<version>.md`)

Lineage: v0.1 (github.com/husky81/mpdx, 2025-12, the model) → v2.0 (CellDocs internal, 2026-08) →
**v2.1 (this document — first public release of the serialization)**.

---

## 0. What MPDX is for

> **A report has one most concise, most beautiful form. What a person writes is the content;
> the form belongs to the system.**

`md+mpdx` is a document **with its formatting removed and its content kept intact**. Prose is
Markdown; tables are MPDX. From an `md+mpdx` file alone, a document editor (CellDocs) can
**reproduce the document** — apply its forms and lay the tables out again.

The reproduced tables **may be arranged differently** from the original: a table split three ways
may come back as one, rows and columns may swap, merged cells may fall elsewhere. What the
document *chose to emphasize* can change. **Its content does not.** Two documents with the same
md+mpdx are the same document.

> 보고서에는 가장 간결하고 아름다운 하나의 형식이 있다. md+mpdx 는 문서의 서식을 제거한 채
> 내용만 그대로 저장한다. 이것만으로 문서를 다시 재현할 수 있어야 한다. 표의 구성이나 표현은
> 달라질 수 있고 문서가 강조하려는 의도도 달라질 수 있지만, 문서의 내용은 같다.

Consequences that the rest of this document follows:

- MPDX stores **meaning**, never layout. Row/column coordinates, `rowspan`/`colspan`, widths,
  borders, colors and fonts are not part of MPDX.
- A value is identified by **what it is the value of** — the intersection of its parents
  (*planned amount* × *student labor* × *institution A*) — not by where it sits.
- Arranging the content into tables is a **projection**, chosen by the reader in context.

---

## 1. Model (unchanged from v0.1)

An MPDX table is a directed acyclic graph of **nodes**.

- Every node has an **id**, a **type**, zero or more **parents**, and optional **text**.
- A node may have **multiple parents**. The graph is not a tree.
- A **value** is a node with **two or more parents**. It means the value at the intersection of
  all its parents' meanings. **Parent order carries no meaning.**
- Labels (headers, categories, item names) are nodes too. A label's parents say what it belongs
  under (*Student labor* under *Labor costs*).
- Nothing in the model implies a grid. A renderer derives one.

---

## 2. The md+mpdx container

An md+mpdx file is Markdown in which tables appear in one of two forms:

| Table | Written as |
|---|---|
| No merged cells | A GitHub-flavored Markdown pipe table |
| Anything else | A fenced block `` ```mpdx `` holding the TSV of §3 |

Markdown carries everything that is not a table: headings (`#`…), paragraphs, lists, equations
(`$$…$$`). CellDocs list styles round-trip through these markers:

| Marker | CellDocs style |
|---|---|
| `□ ` | List 1 |
| `○ ` | List 2 |
| `1. ` | List 3 |
| `- ` | List 4 |
| `* ` | List 5 |
| `1) ` | List 6 |

Inline emphasis is Markdown (`**bold**`, `*italic*`, `~~strike~~`). Whitespace is never placed
inside an emphasis marker.

---

## 3. TSV serialization

### 3.1 Lines

```
# comment lines start with '#'
<id> TAB <parents> TAB <type> TAB <text> [TAB key=value ...]
```

- **id** — positive integer, unique within the block. Ids are assigned per serialization; they are
  addresses for *this* text, not permanent identities (§6).
- **parents** — `0` (root), a single id (`5`), or a list (`[12,4]`, `[12,4,53]`).
- **type** — §3.2.
- **text** — the node's text. Tabs and newlines inside text become spaces.
- **attributes** — optional trailing `key=value` tokens.

The comment header starts with `# MPDX v<version>` and carries a `# spec: <url>` line pointing to
the version of this document that describes it. Everything else in the header is a reading aid.

### 3.2 Node types

| Type | Meaning |
|---|---|
| `tbl` | Table root. Text: `Table <rows> <cols>` optionally followed by `title <title>` (a hint, not content). |
| `t` | Text. A label, or a value when it has two or more parents. |
| `v` | Value (v0.1 spelling). Readers MUST accept it; CellDocs currently writes `t`. |
| `cell` | A multi-paragraph label or value. Its **lines** are the `t` nodes whose **only** parent is this `cell`. |
| `ax` | Stack axis (§5). |
| `block` | A rich cell paragraph (`kind=body\|image\|equation\|list-*`, see §3.5). |
| *(empty)* | Empty cell. Equivalent to `t` with empty text. |

**Line-of-container rule.** A node is a *line* of a `cell` node **iff it has exactly one parent and
that parent is the `cell`**. A node that lists a `cell` among two or more parents is a value or a
label in its own right — not a line.

**Empty values are content.** An empty value (`t` with no text) is a slot that exists and is not
yet filled. It is written, not omitted.

### 3.3 Compaction

Consecutive nodes can share one line:

| Form | Expands to |
|---|---|
| `2:5 ⇥ 1 ⇥ t ⇥ a\|b\|c\|d` | ids 2–5, same parents, texts split on `\|` |
| `27:29 ⇥ [26,4:] ⇥ t ⇥ x\|y\|z` | parents `[26,4]`, `[26,5]`, `[26,6]` |
| `200:203 ⇥ [44,4:,53] ⇥ t ⇥ 98\|97\|\|` | parents `[44,4,53]` … `[44,7,53]` |
| `56:59 ⇥ [18,4:,53] ⇥ t` | four empty values |

Exactly one parent position may carry `:` — it increments by one per id. A text containing `|` is
never compacted. Compaction is notation only; the increment position says nothing about meaning.

### 3.4 Labels and values in practice

A typical budget table:

```
1	0	tbl	Table 3 3
2:4	1	t	Item|Planned|Used
5	1	t	Labor
6	1	t	Materials
7:8	[5,3:]	t	20,000|18,000
9:10	[6,3:]	t	5,000|4,200
```

Node 7 is *Planned* × *Labor*. Whether *Labor* is drawn as a row header and *Planned* as a column
header is the renderer's choice.

> **Non-normative.** CellDocs currently chooses each label's parents from the original table's
> layout (e.g. "the topmost cell of equal width above"). That choice is an implementation detail.
> Readers MUST NOT infer coordinates or spans from it.

### 3.5 Rich cell paragraphs

A `cell` whose content is not plain text holds `block` children:

```
41	[12,4]	cell
42	41	block	본문 문단	kind=body	bid=<uuid>
43	41	block	/media/a.png	kind=image	w=320	h=200
```

`kind` is one of `body`, `list-circle`, `list-dot`, `list-dash`, `list-num`, `list-paren`,
`emphasis`, `image` (`w=`, `h=`), `image-caption` (reserved), `equation` (`latex=`, `script=`).
`bid=` carries the paragraph's stable id when the writer has one. Unknown kinds MUST be preserved.

---

## 4. Reproducing a document

From md+mpdx alone a reader reproduces the document by:

1. Rendering Markdown blocks in order with the target system's forms.
2. For each table, choosing a projection: which labels go to rows, which to columns, and whether a
   stack (§5) becomes one table per layer or a single table. Merged cells follow from the label
   graph (a label that covers several leaves spans them).
3. Placing each value at the intersection of its parents.

Reproduction is **content-exact and layout-free**: every label and value comes back; their
arrangement may not match the original. When the original document is still available (as in a
CellDocs editing session), CellDocs keeps the original arrangement and only replaces content.

---

## 5. Stacks — tables that differ only in their values

Documents often hold several tables with identical labels whose values differ along one more
dimension (a budget table per institution). A **stack** writes the labels once and adds that
dimension as an axis:

```
1	0	tbl	Table 22 10 title 예산사용현황
…	labels, written once …
52	1	ax	구분
53	52	t	주관연구기관	caption=예산사용현황 (주관연구기관)	ptype=List1
54	52	t	공동연구기관-A	caption=예산사용현황 (공동연구기관-A)	ptype=List1
55	52	t	공동연구기관-B	caption=예산사용현황 (공동연구기관-B)	ptype=List1
200:203	[44,4:,53]	t	98,000|97,000||
204:207	[44,4:,54]	t	…
```

- `ax` is the axis; its children are the **layers**.
- A value's parents are **[row label, column label, layer]**.
- Layer attributes: `caption` — the paragraph that titled that table in the source document;
  `ptype` — that paragraph's style. A reader reproducing one table per layer restores these
  captions; md+mpdx omits the caption paragraphs from the Markdown around the block.

The full example is in `examples/budget-three-institutions.stacked.md` (125 lines) next to the
same document written as three separate tables (`….separate.md`, 249 lines).

---

## 6. Patching

To change content, a client sends lines of

```
<id> TAB <new text>
```

using the ids of the MPDX text it read. Ids are reassigned on every serialization, so a client
re-reads before patching. Patching a label changes it everywhere it appears — in a stack, in every
layer. Patching a layer name, the axis or the table root changes nothing (those are not content
slots) and is reported back.

---

## 7. Versioning

- The header names the version (`# MPDX v2.1`) and points to its spec file.
- A version's spec file is never edited after publication except for typos; changes go into a new
  version.
- v0.1 remains at github.com/husky81/mpdx. Later versions are published only at
  https://gitoky.com/bckim/mpdx.

## 8. Changes from v0.1

| v0.1 | v2.1 |
|---|---|
| Root `table`, separate `title` node | Root `tbl`, title as a hint in its text |
| Values are `v` | Values are any node with ≥2 parents; `v` still accepted |
| — | `cell` multi-paragraph nodes and the line-of-container rule |
| — | Range compaction (§3.3) |
| — | Stacks (`ax`, three-parent values) |
| — | md+mpdx container (§2) |
| — | Patch lines (§6) |
