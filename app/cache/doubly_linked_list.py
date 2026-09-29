"""Reusable doubly linked list with head/tail sentinels.

Layout:  head <-> (most recent) ... (least recent) <-> tail
Every operation is O(1).
"""
from __future__ import annotations

from typing import Optional

from .node import Node


class DoublyLinkedList:
    def __init__(self) -> None:
        self.head = Node()  # sentinel
        self.tail = Node()  # sentinel
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def add_to_head(self, node: Node) -> None:
        """Insert node right after the head sentinel (most recent position)."""
        first = self.head.next
        node.prev = self.head
        node.next = first
        self.head.next = node
        first.prev = node
        self._size += 1

    def remove_node(self, node: Node) -> None:
        """Unlink node from the list (node must currently be in this list)."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1

    def pop_tail(self) -> Optional[Node]:
        """Remove and return the least recent node, or None if empty."""
        if self.is_empty():
            return None
        node = self.tail.prev
        self.remove_node(node)
        return node

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size