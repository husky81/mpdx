# src/mpdx/convert/ctl_to_mpdx.py

from mpdx.document import MpdxDocument
from mpdx.node import MpdxNode
from mpdx.layout.ctl import CanonicalTableLayout, Cell


def ctl_to_mpdx(ctl: CanonicalTableLayout) -> MpdxDocument:
    """
    Convert CanonicalTableLayout (CTL) into a layout-preserving MPDX document.

    v0 behavior:
    - Create a single table root node
    - Convert each CTL Cell into a semantic text node (`t`)
    - Preserve layout information in node.meta
    """

    doc = MpdxDocument()

    # 1️⃣ table root node
    table_id = "table_1"
    table_node = MpdxNode(
        id=table_id,
        type="table",
        parents=[],
        meta={
            "n_rows": ctl.n_rows,
            "n_cols": ctl.n_cols,
        },
    )
    doc.add_node(table_node)
    doc.root_id = table_id

    # 2️⃣ cell nodes
    for cell in ctl.cells:
        node_id = f"t_{cell.id}"

        node = MpdxNode(
            id=node_id,
            type="t",
            parents=[table_id],
            text=cell.text,
            meta={
                "row": cell.row,
                "col": cell.col,
                "rowspan": cell.rowspan,
                "colspan": cell.colspan,
                "is_header": cell.is_header,
                "attrs": cell.attrs,
            },
        )

        doc.add_node(node)

    return doc
