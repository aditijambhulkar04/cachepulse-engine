"""Node used by the doubly linked list and both cache implementations."""
from __future__ import annotations

from typing import Any, Optional


class Node:
    """A single cache entry that is also a doubly linked list node."""

    __slots__ = ("key", "value", "frequency", "prev", "next")

    def __init__(self, key: Any = None, value: Any = None, frequency: int = 1) -> None:
        self.key = key
        self.value = value
        self.frequency = frequency
        self.prev: Optional[Node] = None
        self.next: Optional[Node] = None

    def __repr__(self) -> str:
        return f"Node(key={self.key!r}, value={self.value!r}, frequency={self.frequency})"