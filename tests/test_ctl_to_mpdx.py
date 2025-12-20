from mpdx.convert.ctl_to_mpdx import ctl_to_mpdx
from mpdx.layout.parser_html import parse_html_to_ctl


def test_ctl_to_mpdx_basic():
    html = "<table><tr><td>A</td></tr></table>"
    ctl = parse_html_to_ctl(html)
    mp = ctl_to_mpdx(ctl)

    assert mp.root.type == "table"
    assert len(mp.nodes) == 2  # table + cell
