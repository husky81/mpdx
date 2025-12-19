# src\mpdx\io\html.py
# from_html(), to_html() entry

def from_html(path_or_html: str):
    html = read_file_if_needed(path_or_html)
    ctl = parse_html_to_ctl(html)
    mpdx = ctl_to_mpdx(ctl)
    return mpdx