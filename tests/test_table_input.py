import os
import sys
import mpdx
from pathlib import Path
import webbrowser
from dotenv import load_dotenv
load_dotenv()


def test_03():
    mp = mpdx.new()

    mp.writes("비목", "금액", "비고")
    mp.at("비목").writes("직접비", "간접비")

    mp.at("금액").writes(20, 10)

def test_02():
    mp = mpdx.new()
    tbl = mp.write_table()

    mp.writes("비목", "금액", "비고")
    mp.at("비목").writes("직접비", "간접비")
    mp.add_value(20, ["직접비", "금액"])

def test_01(tmp_path):
    mp = mpdx.new()
    
    tbl_node = mp.write_table()
    mp.write_child("비목", "금액", "비고")
    mp.find("비목").add_child("직접비", "간접비")
    mp.write_value(20, ["직접비", "금액"])


    out = tmp_path / "t.html"
    mp.save_html(out)

    open_in_browser_if_requested(out)


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
