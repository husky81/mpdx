import mpdx
import mpdx
from pathlib import Path
from mpdx.io.html import read_html


def test_read_html_from_file(tmp_path):
    p = tmp_path / "a.html"
    p.write_text("<table></table>", encoding="utf-8")

    html = read_html(p)

    assert html == "<table></table>"
