# MPDX Specification — v0.1 (Draft)

**MPDX — Multi-Parent Document Exchange**  
Version: v0.1  
Status: Draft / Experimental  
Last updated: 2025-XX-XX

---

## 1. Introduction

MPDX (Multi-Parent Document Exchange) is a **semantic, graph-based document data model** for representing textual and tabular documents independently of their visual layout.

Unlike traditional document formats that encode documents as trees or fixed grids, MPDX represents documents as **semantic graphs with multi-parent relationships**.  
This enables document meaning to be modeled explicitly and reused across multiple renderings, analyses, and automation pipelines.

This document defines the **core data model and semantics** of MPDX.  
It does **not** mandate a specific file format, encoding, or rendering method.

---

## 2. Design Goals

MPDX is designed with the following goals:

1. **Semantic First**  
   Document meaning should be represented explicitly, not inferred from layout.

2. **Rendering Independence**  
   The same document semantics should support multiple renderings.

3. **Minimal Core Model**  
   The data model should be small, composable, and extensible.

4. **Multi-Parent Semantics**  
   Document elements may belong to multiple semantic contexts simultaneously.

5. **Automation-Friendly**  
   Documents should be directly usable for analysis, transformation, and machine processing.

---

## 3. Conceptual Model

### 3.1 Graph Structure

An MPDX document is a **directed graph** consisting of:

- **Nodes**: semantic units of a document
- **Edges**: parent relationships between nodes

Key properties:

- Nodes MAY have **multiple parents**
- Cycles are **not permitted** in v0.1
- The graph is **not required** to be a tree

---

### 3.2 Node Identity

Each node MUST have:

- A **unique identifier** within the document
- A **type**
- Zero or more **parent references**
- Optional content fields (e.g., text or value)

Node identifiers are opaque and carry no semantic meaning by themselves.

---

## 4. Node Types

MPDX v0.1 defines a minimal set of node types.

Implementations MAY support additional types, but MUST support the following core types.

### 4.1 `table`

Represents the root of a document or a logical table.

Properties:
- SHOULD have no parents (except in nested documents)
- Serves as the primary semantic container

---

### 4.2 `title`

Represents a title associated with a table or document.

Properties:
- MUST have exactly one parent of type `table`
- Contains human-readable text

---

### 4.3 `t` (Semantic Text Node)

Represents semantic labels such as:

- Headers
- Categories
- Dimensions
- Descriptive items

Properties:
- MAY have one or more parents
- Text content SHOULD be human-readable
- Semantics are defined by parent relationships

---

### 4.4 `v` (Value Node)

Represents a concrete value resulting from a **semantic intersection**.

Properties:
- MUST have two or more parents
- Represents the combination of all parent semantics
- Content MAY be numeric, textual, or structured

A value node MUST NOT be interpreted as a positional cell.

---

## 5. Semantic Intersections

In MPDX, meaning emerges from **parent combinations**.

A value node with parents:

- P₁, P₂, …, Pₙ

is interpreted as:

> “The value corresponding to the intersection of the semantics represented by P₁…Pₙ.”

The order of parents is **not significant**.

---

## 6. Document Semantics

### 6.1 No Implicit Layout

MPDX does not encode:

- Rows or columns
- Visual positions
- Cell coordinates
- Rendering instructions

Any layout is a **projection** derived from the semantic graph.

---

### 6.2 Multiple Valid Projections

The same MPDX document may be rendered as:

- Hierarchical tables
- Flat analytical tables
- Pivoted or transposed views
- Graph queries or database tables

All projections MUST preserve the same underlying semantics.

---

## 7. Serialization (Non-Normative)

MPDX is independent of any specific serialization format.

A **TSV-based reference serialization** is provided in this repository for:

- Human readability
- Example sharing
- Intermediate representation

This serialization is **informative, not normative**.

Implementations MAY define alternative serializations such as:

- JSON
- YAML
- Binary formats
- Graph databases

---

## 8. Validation Rules (v0.1)

An MPDX document is considered valid if:

1. All node identifiers are unique
2. All parent references resolve to existing nodes
3. No cycles exist in the parent graph
4. Node types conform to this specification
5. `v` nodes have at least two parents

---

## 9. Versioning and Compatibility

- v0.x versions are **experimental**
- Breaking changes MAY occur
- Backward compatibility is **not guaranteed** before v1.0

Future versions will define:

- Stability guarantees
- Extension mechanisms
- Compatibility rules

---

## 10. Open Questions (Non-Normative)

The following topics are intentionally left open in v0.1:

- Typed values (numeric vs string vs structured)
- Units and metadata
- Query languages
- Constraint schemas
- Rendering standards

These are expected to evolve through discussion and experimentation.

---

## 11. Conformance

An implementation conforms to MPDX v0.1 if it:

- Correctly represents the node types defined in this specification
- Preserves multi-parent semantic relationships
- Does not introduce implicit positional semantics

---

## 12. Status

This specification is an **early draft** released to:

- Establish a shared conceptual model
- Enable discussion and experimentation
- Support academic reference and extension

Feedback and contributions are welcome.

---

## 13. License

This specification is released under the same license as the MPDX repository.

---

*MPDX is not a document format.*  
*It is a semantic document model.*
