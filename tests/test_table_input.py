import os
import sys
import mpdx
from pathlib import Path
import webbrowser
from dotenv import load_dotenv
load_dotenv()


def test_01(tmp_path):
    mp = mpdx.new()

    

    out = tmp_path / "t.html"
    mp.save_html(out)

    open_in_browser_if_requested(inp)
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
