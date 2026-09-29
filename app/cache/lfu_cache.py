"""True O(1) LFU cache.

Structures:
  key_map  : key -> Node
  freq_map : frequency -> DoublyLinkedList (head = most recent within bucket)
  min_freq : smallest frequency currently present

Ties on frequency are broken by evicting the least recently used key
(the tail of the min_freq bucket).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .doubly_linked_list import DoublyLinkedList
from .node import Node


class LFUCache:
    def __init__(self, capacity: int) -> None:
        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self.key_map: Dict[Any, Node] = {}
        self.freq_map: Dict[int, DoublyLinkedList] = {}
        self.min_freq = 0
        self.hits = 0
        self.misses = 0
        self.last_evicted: Optional[Any] = None

    def _touch(self, node: Node) -> None:
        """Move node from its frequency bucket to frequency + 1. O(1)."""
        old_freq = node.frequency
        bucket = self.freq_map[old_freq]
        bucket.remove_node(node)
        if bucket.is_empty():
            del self.freq_map[old_freq]
            if self.min_freq == old_freq:
                self.min_freq += 1
        node.frequency = old_freq + 1
        self._bucket(node.frequency).add_to_head(node)

    def _bucket(self, freq: int) -> DoublyLinkedList:
        bucket = self.freq_map.get(freq)
        if bucket is None:
            bucket = self.freq_map[freq] = DoublyLinkedList()
        return bucket

    def _evict(self) -> None:
        bucket = self.freq_map[self.min_freq]
        victim = bucket.pop_tail()  # LRU among lowest-frequency keys
        if bucket.is_empty():
            del self.freq_map[self.min_freq]
        del self.key_map[victim.key]
        self.last_evicted = victim.key

    def get(self, key: Any) -> Optional[Any]:
        node = self.key_map.get(key)
        if node is None:
            self.misses += 1
            return None
        self.hits += 1
        self._touch(node)
        return node.value

    def put(self, key: Any, value: Any) -> None:
        """Insert/update. Does not affect hit/miss statistics.

        Updating an existing key counts as a use (frequency + 1).
        """
        self.last_evicted = None
        node = self.key_map.get(key)
        if node is not None:
            node.value = value
            self._touch(node)
            return
        if len(self.key_map) >= self.capacity:
            self._evict()
        node = Node(key, value, frequency=1)
        self.key_map[key] = node
        self._bucket(1).add_to_head(node)
        self.min_freq = 1

    def delete(self, key: Any) -> bool:
        """Remove a key. Returns False if it was not present. O(1).

        min_freq may become stale if the last lowest-frequency key is removed.
        That is safe: eviction only happens when the cache is full, and the
        only way to become full again is inserting a new key, which resets
        min_freq to 1.
        """
        node = self.key_map.pop(key, None)
        if node is None:
            return False
        bucket = self.freq_map[node.frequency]
        bucket.remove_node(node)
        if bucket.is_empty():
            del self.freq_map[node.frequency]
        if not self.key_map:
            self.min_freq = 0
        return True

    def __contains__(self, key: Any) -> bool:
        """Membership check without touching frequency or stats."""
        return key in self.key_map

    def frequency_of(self, key: Any) -> Optional[int]:
        node = self.key_map.get(key)
        return None if node is None else node.frequency

    @property
    def size(self) -> int:
        return len(self.key_map)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return 0.0 if total == 0 else self.hits / total * 100

    def stats(self) -> Dict[str, Any]:
        return {
            "policy": "LFU",
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "capacity": self.capacity,
            "size": self.size,
        }