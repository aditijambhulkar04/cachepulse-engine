"""O(1) LRU cache: hash map + doubly linked list."""
from __future__ import annotations

from typing import Any, Dict, Optional

from .doubly_linked_list import DoublyLinkedList
from .node import Node


class LRUCache:
    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self.key_map: Dict[Any, Node] = {}
        self.list = DoublyLinkedList()  # head = MRU, tail = LRU
        self.hits = 0
        self.misses = 0
        self.last_evicted: Optional[Any] = None

    def get(self, key: Any) -> Optional[Any]:
        node = self.key_map.get(key)
        if node is None:
            self.misses += 1
            return None
        self.hits += 1
        self.list.remove_node(node)
        self.list.add_to_head(node)
        return node.value

    def put(self, key: Any, value: Any) -> None:
        """Insert/update. Does not affect hit/miss statistics."""
        self.last_evicted = None
        node = self.key_map.get(key)
        if node is not None:
            node.value = value
            self.list.remove_node(node)
            self.list.add_to_head(node)
            return
        if len(self.key_map) >= self.capacity:
            evicted = self.list.pop_tail()
            del self.key_map[evicted.key]
            self.last_evicted = evicted.key
        node = Node(key, value)
        self.key_map[key] = node
        self.list.add_to_head(node)

    def delete(self, key: Any) -> bool:
        """Remove a key. Returns False if it was not present. O(1)."""
        node = self.key_map.pop(key, None)
        if node is None:
            return False
        self.list.remove_node(node)
        return True

    def __contains__(self, key: Any) -> bool:
        """Membership check without touching recency or stats."""
        return key in self.key_map

    @property
    def size(self) -> int:
        return len(self.key_map)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return 0.0 if total == 0 else self.hits / total * 100

    def stats(self) -> Dict[str, Any]:
        return {
            "policy": "LRU",
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "capacity": self.capacity,
            "size": self.size,
        }