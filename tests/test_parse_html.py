from mpdx.layout.parser_html import HtmlTableParser


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
