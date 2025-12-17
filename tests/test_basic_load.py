import mpdx
from mpdx import KanType

def test_first_kan_is_table():
    m = mpdx.load("samples/plan_3x3.mpdx")
    assert m.kans[0].type is KanType.Table
