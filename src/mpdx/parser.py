from pathlib import Path
import re
from typing import Union
from .kan import Kan, KanType
from .mpis import MPIS



def parse_mpdx(path: str | Path) -> MPIS:
    path = Path(path)
    kans = []

    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue

        cols = re.split(r"\t+", s)
        if not cols[0].isdigit():
            continue

        kid = int(cols[0])
        parents = _parse_parents(cols[1])
        ktype = _parse_type(cols[2])
        text = cols[3] if len(cols) > 3 else ""

        kans.append(Kan(
            id=kid,
            type=ktype,
            parents=parents,
            text=text
        ))

    return MPIS(kans)


def _parse_parents(raw: str) -> tuple[int, ...]:
    raw = raw.strip()
    if raw.startswith("["):
        return tuple(int(x.strip()) for x in raw[1:-1].split(","))
    return (int(raw),)


def _parse_type(t: str) -> KanType:
    return {
        "table": KanType.Table,
        "title": KanType.Title,
        "t": KanType.Text,
        "v": KanType.Value,
    }[t]
