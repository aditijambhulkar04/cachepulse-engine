"""Selects and fronts an LRU or LFU cache."""
from __future__ import annotations

from typing import Any, Dict, Optional, Union

from .lfu_cache import LFUCache
from .lru_cache import LRUCache

DEFAULT_POLICY = "LFU"
DEFAULT_CAPACITY = 50

_POLICIES = {"LRU": LRUCache, "LFU": LFUCache}


class CacheManager:
    def __init__(self, policy: str = DEFAULT_POLICY, capacity: int = DEFAULT_CAPACITY) -> None:
        self.policy = self._normalize(policy)
        self.capacity = capacity
        self.cache: Union[LRUCache, LFUCache] = _POLICIES[self.policy](capacity)

    @staticmethod
    def _normalize(policy: str) -> str:
        name = str(policy).strip().upper()
        if name not in _POLICIES:
            raise ValueError(f"Unknown policy {policy!r}; choose from {list(_POLICIES)}")
        return name

    def get(self, key: Any) -> Optional[Any]:
        return self.cache.get(key)

    def put(self, key: Any, value: Any) -> None:
        self.cache.put(key, value)

    def delete(self, key: Any) -> bool:
        return self.cache.delete(key)

    def clear(self) -> int:
        """Remove all entries and reset statistics. Returns entries removed."""
        removed = self.cache.size
        self.reset()
        return removed

    def __contains__(self, key: Any) -> bool:
        return key in self.cache

    def stats(self) -> Dict[str, Any]:
        return self.cache.stats()

    def reset(self, policy: Optional[str] = None, capacity: Optional[int] = None) -> None:
        """Replace the underlying cache (optionally switching policy/capacity).

        Existing entries and statistics are discarded.
        """
        self.policy = self._normalize(policy) if policy is not None else self.policy
        self.capacity = capacity if capacity is not None else self.capacity
        self.cache = _POLICIES[self.policy](self.capacity)