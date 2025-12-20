# src\mpdx\layout\parser.py
# HTML → CTL

from bs4 import BeautifulSoup
from typing import List
from .ctl import Cell, CanonicalTableLayout


class HtmlTableParser:
    """
    Parse a single HTML <table> element into a CanonicalTableLayout (CTL).

    Responsibilities:
    - Interpret rowspan / colspan
    - Preserve original cell layout
    - Extract plain text content
    """

    def parse(self, html: str) -> CanonicalTableLayout:
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table")
        if table is None:
            raise ValueError("No <table> element found in HTML")

        rows = table.find_all("tr")

        cells: List[Cell] = []
        owner: List[List[str]] = []

        current_row = 0
        cell_id_counter = 1

        for tr in rows:
            # ensure owner has a row
            if len(owner) <= current_row:
                owner.append([])

            col_idx = 0
            tds = tr.find_all(["td", "th"])

            for td in tds:
                # skip already-occupied columns (rowspan spillover)
                while col_idx < len(owner[current_row]) and owner[current_row][col_idx] is not None:
                    col_idx += 1

                rowspan = int(td.get("rowspan", 1))
                colspan = int(td.get("colspan", 1))

                cell_id = f"c{cell_id_counter}"
                cell_id_counter += 1

                text = td.get_text(strip=True)
                is_header = td.name.lower() == "th"

                cell = Cell(
                    id=cell_id,
                    row=current_row,
                    col=col_idx,
                    rowspan=rowspan,
                    colspan=colspan,
                    text=text,
                    is_header=is_header,
                    attrs=dict(td.attrs),
                )
                cells.append(cell)

                # mark ownership in grid
                for r in range(current_row, current_row + rowspan):
                    while len(owner) <= r:
                        owner.append([])

                    for c in range(col_idx, col_idx + colspan):
                        while len(owner[r]) <= c:
                            owner[r].append(None)

                        owner[r][c] = cell_id

                col_idx += colspan

            current_row += 1

        # normalize column count
        n_rows = len(owner)
        n_cols = max(len(row) for row in owner) if owner else 0

        for row in owner:
            while len(row) < n_cols:
                row.append(None)

        return CanonicalTableLayout(
            n_rows=n_rows,
            n_cols=n_cols,
            cells=cells,
            owner=owner,
        )

def parse_html_to_ctl(html: str) -> CanonicalTableLayout:
    """
    Parse HTML string containing a <table> element
    into a CanonicalTableLayout (CTL).

    This function assumes that the HTML has already been loaded
    and normalized (e.g. via read_html).
    """
    parser = HtmlTableParser()
    return parser.parse(html)