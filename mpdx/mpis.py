from __future__ import annotations
from typing import Dict, List, Iterable
from .kan import Kan, KanType


class MPIS:
    def __init__(self, kans: Iterable[Kan]):
        self._kans: List[Kan] = list(kans)
        self._by_id: Dict[int, Kan] = {k.id: k for k in self._kans}

        if len(self._by_id) != len(self._kans):
            raise ValueError("Duplicate Kan id detected")

    @property
    def kans(self) -> List[Kan]:
        return self._kans

    def get(self, kan_id: int) -> Kan:
        return self._by_id[kan_id]

    def children_of(self, kan_id: int) -> List[Kan]:
        return [k for k in self._kans if kan_id in k.parents]

    def parents_of(self, kan_id: int) -> List[Kan]:
        k = self.get(kan_id)
        return [self._by_id[p] for p in k.parents if p in self._by_id]

    def first(self, kan_type: KanType) -> Kan:
        for k in self._kans:
            if k.type is kan_type:
                return k
        raise LookupError(f"No Kan of type {kan_type}")

    def all(self, kan_type: KanType) -> List[Kan]:
        return [k for k in self._kans if k.type is kan_type]
