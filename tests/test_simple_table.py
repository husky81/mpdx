import mpdx
import mpdx
from pathlib import Path


def test_simple_table_load2():
    path = Path("examples/3x3_table.html")

    mp = mpdx.load(path)

    assert mp is not None


def test_simple_table_roundtrip():
    path = Path("examples/3x3_table.html")

    mp = mpdx.load(path)
    html_out = mp.to_html()

    assert "<table" in html_out.lower()
    assert "</table>" in html_out.lower()


def test_simple_table(self):
    mp = mpdx.load("examples\3x3_table.html")

def test_simple_table_load():
    path = Path("examples/3x3_table.html")

    mp = mpdx.load(path)

    assert mp is not None