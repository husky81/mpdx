# MPDX (Multi-Parent Document Exchange)

MPDX is a **semantic, graph-based document data model** designed to represent textual and tabular documents independently of their visual layout.  
It enables documents—especially complex tables—to be modeled as **meaning-centered structures**, allowing the same document semantics to be rendered, queried, and reused in multiple forms.

This repository provides the **reference specification, examples, and minimal tooling** for MPDX.

---

## Motivation

Most existing document formats (e.g., DOCX, HTML, spreadsheets) encode documents as:

- Tree-based structures (DOM, XML)
- Row–column–oriented tables
- Layout-driven representations

While effective for rendering, these formats make it difficult to:

- Explicitly represent **semantic relationships** between document elements
- Reuse document meaning across different layouts
- Apply documents directly to automation, analysis, or LLM-based processing

In particular, **table cells are typically defined by coordinates**, not by meaning.

MPDX addresses this limitation by modeling documents as **semantic graphs with multi-parent relationships**, where values are defined as intersections of semantic axes rather than fixed positions.

---

## Core Concepts

### 1. Semantic Graph Model
- All document elements are represented as **nodes**
- Nodes may have **multiple parents**, enabling semantic intersections
- The model is not constrained to tree structures

### 2. Minimal Node Types
MPDX intentionally defines only a small set of node types:

| Type | Description |
|-----|------------|
| `table` | Root node representing a document or table |
| `title` | Title of a document or table |
| `t` | Semantic text node (headers, labels, items) |
| `v` | Value node representing a semantic intersection |

### 3. Values as Semantic Intersections
A value is not “row × column”, but the result of combining multiple meanings.

Example:
- Parent A: *Student Labor*
- Parent B: *Planned Amount*

→ Value represents **“Planned amount of student labor”**

---

## MPDX Serialization

MPDX can be serialized in a simple, human-readable, text-based format.

- Tab-separated (TSV) reference serialization
- Each row represents a node
- Parent relationships are explicitly listed
- Suitable as an **intermediate representation**

Example:

```text
id	parents	type	text
1	0	table
2	1	title	Simple Budget Example
3	2	t	Category
4	2	t	Item
5	2	t	Planned Amount
10	3	t	Direct Cost
11	[10,4]	t	Student Labor
12	[11,5]	v	20000
