import mpdx

mp = mpdx.load("examples/3x3_table.html")
html_out = mp.to_html()
print(html_out)
