import os
import sys
import mpdx
from pathlib import Path
import webbrowser
from dotenv import load_dotenv

load_dotenv()

def open_in_browser_if_requested(path: Path):
    """
    Test-only helper.
    Opens HTML in default browser on Windows when explicitly enabled.
    """
    # 1) Windows only
    if sys.platform != "win32":
        return

    # 2) Only when user explicitly allows it
    #   PowerShell:
    #     $env:MPDX_OPEN_HTML=1
    flag = os.environ.get("MPDX_OPEN_HTML", "").lower()
    if flag not in {"1", "true", "yes", "on"}:
        return

    webbrowser.open(path.resolve().as_uri())


def test_01(tmp_path):
    inp = Path("examples/3x3_table.html")
    mp = mpdx.load(inp)
    out = tmp_path / "t.html"
    mp.save_html(out)
    assert out.exists()

    open_in_browser_if_requested(inp)
    open_in_browser_if_requested(out)

def test_simple_table_load2():
    path = Path("examples/3x3_table.html")
    mp = mpdx.load(path)
    html_str = mp.to_html()
    print(mp)


def test_save_mpdx(tmp_path):
    mp = mpdx.load("examples/3x3_table.html")

    out = tmp_path / "table.mpdx"
    mp.save(out)

    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "table_1" in content


def test_simple_table_roundtrip():
    path = Path("examples/3x3_table.html")

    mp = mpdx.load(path)
    html_out = mp.to_html()

    assert "<table" in html_out.lower()
    assert "</table>" in html_out.lower()


def test_simple_table_load():
    path = Path("examples/3x3_table.html")

    mp = mpdx.load(path)

    assert mp is not None
