import mpdx

def test_first_kan_is_table():
    m = mpdx.load("samples/plan_3x3.mpdx")
    assert m.kans[0].type is KanType.Table

def test_load(self):
    mp = mpdx.load("a.html")
    

def test_round_trip(self):
    html = load_html()

    # HTML → CTL
    ctl1 = HtmlTableParser().parse(html)

    # CTL → MPDX
    mpdx = CtLtoMpdxConverter().convert(ctl1)

    # (여기서 MPDX 조작 가능)
    # mpdx.nodes["t_12"].text = "Updated Value"

    # MPDX → CTL
    ctl2 = MpdxToCtlConverter().convert(mpdx)

    # CTL → HTML
    html_out = HtmlTableRenderer().render(ctl2)

def test_mani(self):
    mp = mpdx.from_html("a.html")

    mp.nodes            # 모든 노드
    mp.root             # table node
    mp.find(type="t")   # 텍스트 노드
    mp.to_html()        # 다시 HTML로

def test_ex(self):
    mp = mpdx.from_html("a.html", preserve_layout=True)
    mp = mpdx.from_html("a.html", infer_semantics=True)

    mp = mpdx.from_html(html_string)
    mp = mpdx.from_html(file_like_object)
