아래는 **표준 포맷/모델 프로젝트 톤**에 맞게 정리하고,
중복·구조 깨짐·논문 초안 느낌을 제거한 **개선된 README.md 버전**입니다.
(의미는 유지하면서 *“표준 후보 + 오픈 프로젝트”* 인상을 강화했습니다.)

---

````markdown
# MPDX — Multi-Parent Document Exchange

MPDX is a **semantic, graph-based document data model** for representing textual and tabular documents independently of visual layout.

Rather than encoding documents as trees or grid coordinates, MPDX models documents as **meaning-centered semantic graphs**, enabling the same document semantics to be rendered, queried, analyzed, and reused across multiple forms.

This repository provides the **reference specification, examples, and minimal tooling** for MPDX.

---

## Motivation

Most existing document formats—such as DOCX, HTML, and spreadsheets—encode documents as:

- Tree-based structures (DOM, XML)
- Row–column–oriented tables
- Layout-driven representations

While effective for rendering, these approaches make it difficult to:

- Explicitly represent **semantic relationships** between document elements
- Reuse document meaning across different layouts
- Apply documents directly to automation, analysis, or LLM-based processing

In particular, **tabular data is usually defined by coordinates**, not by meaning.  
A cell is typically identified as “row × column,” even when its true meaning is a semantic combination (e.g., *planned amount* × *student labor*).

MPDX addresses this limitation by modeling documents as **semantic graphs with multi-parent relationships**, where values are defined by **semantic intersections**, not fixed positions.

---

## Core Concepts

### 1. Semantic Graph Model

- All document elements are represented as **nodes**
- Nodes may have **multiple parents**, enabling semantic intersections
- The model is not constrained to tree structures

This allows document meaning to be expressed directly, rather than inferred from layout.

---

### 2. Minimal Node Types

MPDX intentionally defines a small, extensible set of node types:

| Type   | Description |
|------|------------|
| `table` | Root node representing a document or table |
| `title` | Title of a document or table |
| `t` | Semantic text node (headers, labels, categories) |
| `v` | Value node representing a semantic intersection |

---

### 3. Values as Semantic Intersections

In MPDX, a value is not defined as “row × column,” but as the intersection of multiple semantic dimensions.

**Example:**

- Parent A: *Student Labor*
- Parent B: *Planned Amount*

→ The resulting value represents:  
**“Planned amount of student labor”**

This interpretation is independent of how the table is visually arranged.

---

## MPDX Serialization

MPDX can be serialized using simple, human-readable, text-based formats.

This repository includes a **TSV-based reference serialization**:

- Each row represents a node
- Parent relationships are explicitly listed
- Designed as an **intermediate representation**, not a final rendering format

**Example:**

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
````

The serialization format is only one possible representation.
**MPDX as a model is not tied to any specific file format.**

---

## Rendering Independence

A key property of MPDX is the separation of **meaning** and **rendering**.

The same MPDX data can be rendered as:

* Hierarchical tables with merged cells
* Fully flattened analytical tables
* Pivoted or transposed views
* Database-friendly representations

All of these are different projections of the same underlying semantic model.

---

## Use Cases

* Document automation and transformation
* Complex table modeling (budgets, reports, forms)
* LLM-friendly document structuring
* Semantic document analysis
* Intermediate representation between authoring and rendering
* Database-backed document systems

---

## Project Status

MPDX is currently in an **early, research-oriented stage**.

* The core data model is stable enough for experimentation
* Reference serialization and examples are provided
* Tooling is intentionally minimal

This repository is published to:

* Establish the conceptual model
* Enable discussion and early adoption
* Support academic reference and extension

---

## Related Publication

This repository accompanies the research paper:

***A Semantic Graph-Based Document Model for Tabular and Textual Data***
**MPDX: A Multi-Parent Document Exchange Format**

(Preprint / publication details will be added.)

---

## Contributing

MPDX is an open research and standardization-oriented project.
Contributions, discussions, and experimental implementations are welcome.

Suggested contribution areas include:

* Alternative serializations
* Rendering rules
* Query models
* Tooling and converters
* Case studies and real-world applications

---

## License

This project is released under the **MIT License**.

---

## Contact

For questions, discussion, or collaboration:

* GitHub Issues
* Pull Requests

---

**MPDX is not a document format.**
**It is a semantic document model.**

```

---

### 다음 단계로 추천하는 개선 (선택)
- `spec/` 디렉토리에 **MPDX v0.1 Spec** 문서 분리
- README 상단에 **“Open standard candidate”** 문구 추가
- LICENSE를 Apache-2.0으로 변경 고려 (표준 확산 목적이라면)

원하면 다음도 바로 도와줄 수 있어요:
- 📘 **MPDX 공식 스펙 문서 템플릿**
- 🧠 논문 abstract (표준 제안용 톤)
- 🗺️ v1.0까지의 로드맵

어디까지 같이 다듬을까요?
```
