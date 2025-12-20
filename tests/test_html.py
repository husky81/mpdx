import mpdx
import mpdx
from pathlib import Path
from mpdx.io.html import read_html
from mpdx.layout.parser_html import HtmlTableParser


def test_read_html_from_file(tmp_path):
    p = tmp_path / "a.html"
    p.write_text("<table></table>", encoding="utf-8")

    html = read_html(p)

    assert html == "<table></table>"

def test_save_html(tmp_path):
    mp = mpdx.load("examples/3x3_table.html")

    out = tmp_path / "table.html"
    out.write_text(mp.to_html(), encoding="utf-8")

    assert out.exists()
    assert "<table" in out.read_text(encoding="utf-8").lower()

def test_simple_3x3_with_merge():
    html = """
    <table>
      <tr>
        <th rowspan="2">Group</th>
        <th colspan="2">Quarter</th>
      </tr>
      <tr>
        <th>Q1</th>
        <th>Q2</th>
      </tr>
      <tr>
        <td>A</td>
        <td>10</td>
        <td>12</td>
      </tr>
    </table>
    """

    ctl = HtmlTableParser().parse(html)

    assert ctl.n_rows == 3
    assert ctl.n_cols == 3
    assert len(ctl.cells) == 7
