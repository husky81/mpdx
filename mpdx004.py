from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, List
import html
import re
from pathlib import Path



def compute_rowspans(rows, columns):
    """
    rows: List[Dict[col_id, value]]
    columns: ordered list of column ids to consider for rowspan
    returns:
      rowspan_map[(row_index, col_id)] = rowspan
      hidden_cells = set((row_index, col_id))
    """
    rowspan_map = {}
    hidden = set()

    row_count = len(rows)

    for col_idx, col in enumerate(columns):
        i = 0
        while i < row_count:
            val = rows[i].get(col)
            if val in (None, ""):
                rowspan_map[(i, col)] = 1
                i += 1
                continue

            span = 1
            for j in range(i + 1, row_count):
                # 상위 컬럼이 다르면 병합 중단
                for parent_col in columns[:col_idx]:
                    if rows[j].get(parent_col) != rows[i].get(parent_col):
                        break
                else:
                    if rows[j].get(col) == val:
                        span += 1
                        continue
                break

            rowspan_map[(i, col)] = span
            for k in range(i + 1, i + span):
                hidden.add((k, col))

            i += span

    return rowspan_map, hidden


rowspan_map, hidden_cells = compute_rowspans(rows, merge_columns)

for r_idx, row in enumerate(rows):
    print("<tr>")
    for col in all_columns:
        if (r_idx, col) in hidden_cells:
            continue

        span = rowspan_map.get((r_idx, col), 1)
        if span > 1:
            print(f'<td rowspan="{span}">{row[col]}</td>')
        else:
            print(f'<td>{row[col]}</td>')
    print("</tr>")
