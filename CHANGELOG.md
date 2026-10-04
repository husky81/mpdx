# Changelog

## v2.2 — 2026-10-05

md+mpdx is a **static snapshot** (spec §0.1): writers record the value the reader sees on screen
(display formats applied) and never emit formulas, function chips or field placeholders; a value
that cannot be computed is written as a visible marker. Readers import computed cells as values.
The serialization itself is unchanged — v2.1 readers read v2.2 output. Published at
https://gitoky.com/bckim/mpdx (spec/mpdx-v2.2.md).

## v2.1 — 2026-10-04
First public release of the serialization CellDocs emits. Published at
https://gitoky.com/bckim/mpdx (spec/mpdx-v2.1.md). From here on, new versions are published only there.

- md+mpdx container: Markdown prose + MPDX tables, round-tripping CellDocs list styles.
- `cell` multi-paragraph nodes and the line-of-container rule.
- Range compaction with one incrementing parent position (`[44,4:,53]`).
- Stacks: tables with identical labels written once, with an `ax` axis and three-parent values.
- Patch lines `<id> TAB <new text>`.
- Output header carries `# spec: <url>`.

## v2.0 — 2026-08 (CellDocs internal, unpublished)
TSV serialization with multi-parent nodes used by the CellDocs editor and its MCP tools.

## v0.1 — 2025-12-19
The model: semantic graph, multi-parent nodes, values as semantic intersections, rendering
independence. github.com/husky81/mpdx.
