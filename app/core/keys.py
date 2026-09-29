"""Path-key helpers (framework independent).

Cache keys may be int or str. In a URL path everything is text, so
`/cache/101` could mean the int 101 or the string "101". We try the int
form first (only when it is canonical, e.g. "101" but not "007"), then
the string form.
"""
from __future__ import annotations

from typing import List, Union

Key = Union[int, str]


def candidate_keys(raw: str) -> List[Key]:
    candidates: List[Key] = []
    try:
        as_int = int(raw)
        if str(as_int) == raw:
            candidates.append(as_int)
    except ValueError:
        pass
    candidates.append(raw)
    return candidates