"""Three data structures built from scratch: a doubly linked list, a hash map and a
binary search tree.

None of them use Python's dict or set, or a list's search and sort methods. Python lists
appear in three plain roles only: a fixed-length array of buckets in the hash map (the
same role a Java array plays), the array `to_array()` hands to the sorting algorithms,
and a stack (push and pop at one end) for walking the tree.

The loops are iterative instead of recursive, so a tall tree or a long list cannot hit
Python's recursion limit.
"""

from typing import Callable, Iterator, Optional

from .interfaces import ListADT, MapADT, SortedMapADT


# ── Doubly linked list ────────────────────────────────────────────────

class _ListNode:
    __slots__ = ("element", "prev", "next")

    def __init__(self, element, prev=None, next=None):
        self.element = element
        self.prev = prev
        self.next = next


class DoublyLinkedList(ListADT):
    """Each node points to the one before and the one after it.

    | Operation | Cost |
    |---|---|
    | add or remove at either end | O(1) |
    | get(index) | O(n), walks from the nearer end |
    | remove_if, iteration | O(n) |
    """

    def __init__(self, elements=()):
        self._head: Optional[_ListNode] = None
        self._tail: Optional[_ListNode] = None
        self._size = 0
        for element in elements:
            self.add_last(element)

    def add_first(self, element) -> None:
        node = _ListNode(element, None, self._head)
        if self._head is None:
            self._tail = node
        else:
            self._head.prev = node
        self._head = node
        self._size += 1

    def add_last(self, element) -> None:
        node = _ListNode(element, self._tail, None)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def remove_first(self):
        if self._head is None:
            raise IndexError("remove_first from an empty list")
        node = self._head
        self._unlink(node)
        return node.element

    def remove_last(self):
        if self._tail is None:
            raise IndexError("remove_last from an empty list")
        node = self._tail
        self._unlink(node)
        return node.element

    def first(self):
        if self._head is None:
            raise IndexError("first of an empty list")
        return self._head.element

    def last(self):
        if self._tail is None:
            raise IndexError("last of an empty list")
        return self._tail.element

    def get(self, index: int):
        if not 0 <= index < self._size:
            raise IndexError(f"index {index} is outside 0..{self._size - 1}")
        if index < self._size // 2:
            node = self._head
            for _ in range(index):
                node = node.next
        else:
            node = self._tail
            for _ in range(self._size - 1 - index):
                node = node.prev
        return node.element

    def remove_if(self, predicate: Callable) -> int:
        removed = 0
        node = self._head
        while node is not None:
            following = node.next
            if predicate(node.element):
                self._unlink(node)
                removed += 1
            node = following
        return removed

    def _unlink(self, node: _ListNode) -> None:
        if node.prev is None:
            self._head = node.next
        else:
            node.prev.next = node.next
        if node.next is None:
            self._tail = node.prev
        else:
            node.next.prev = node.prev
        node.prev = node.next = None
        self._size -= 1

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator:
        node = self._head
        while node is not None:
            yield node.element
            node = node.next

    def __reversed__(self) -> Iterator:
        node = self._tail
        while node is not None:
            yield node.element
            node = node.prev

    def to_array(self) -> list:
        """The elements in list order, as an array for the sorting algorithms."""
        array = [None] * self._size
        i = 0
        for element in self:
            array[i] = element
            i += 1
        return array

    def __repr__(self) -> str:
        return f"DoublyLinkedList(size={self._size})"


# ── Hash map ──────────────────────────────────────────────────────────

FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
MASK_64 = (1 << 64) - 1


def fnv1a(key) -> int:
    """64-bit FNV-1a hash of the key's text. The type name is part of the text, so the
    number 1 and the string "1" get different hashes."""
    h = FNV_OFFSET
    for byte in f"{type(key).__name__}:{key}".encode("utf-8"):
        h = ((h ^ byte) * FNV_PRIME) & MASK_64
    return h ^ (h >> 32)  # fold the high bits in, because the bucket index uses only the low ones


class _Entry:
    __slots__ = ("key", "value", "hash", "next")

    def __init__(self, key, value, hash_, next=None):
        self.key = key
        self.value = value
        self.hash = hash_
        self.next = next


class HashMap(MapADT):
    """Separate chaining: each bucket holds a small linked chain of entries.

    The number of buckets is a power of two and doubles when the map is more than
    75% full, so chains stay short.

    | Operation | Average | Worst case (every key in one bucket) |
    |---|---|---|
    | put, get, remove | O(1) | O(n) |
    | resize | O(n), but rare, so O(1) spread over all puts | |
    """

    MAX_LOAD = 0.75

    def __init__(self, capacity: int = 16, hash_function: Callable = fnv1a):
        if capacity < 1 or capacity & (capacity - 1):
            raise ValueError("capacity must be a power of two")
        self._buckets = [None] * capacity
        self._size = 0
        self._hash = hash_function
        self.resizes = 0

    @property
    def capacity(self) -> int:
        return len(self._buckets)

    def _index(self, h: int) -> int:
        return h & (len(self._buckets) - 1)

    def _find(self, key, h):
        entry = self._buckets[self._index(h)]
        while entry is not None:
            if entry.hash == h and entry.key == key:
                return entry
            entry = entry.next
        return None

    def put(self, key, value):
        h = self._hash(key)
        entry = self._find(key, h)
        if entry is not None:
            old, entry.value = entry.value, value
            return old
        i = self._index(h)
        self._buckets[i] = _Entry(key, value, h, self._buckets[i])
        self._size += 1
        if self._size > self.MAX_LOAD * len(self._buckets):
            self._resize(2 * len(self._buckets))
        return None

    def get(self, key, default=None):
        entry = self._find(key, self._hash(key))
        return default if entry is None else entry.value

    def remove(self, key):
        h = self._hash(key)
        i = self._index(h)
        prev, entry = None, self._buckets[i]
        while entry is not None:
            if entry.hash == h and entry.key == key:
                if prev is None:
                    self._buckets[i] = entry.next
                else:
                    prev.next = entry.next
                self._size -= 1
                return entry.value
            prev, entry = entry, entry.next
        return None

    def _resize(self, capacity: int) -> None:
        old = self._buckets
        self._buckets = [None] * capacity
        for head in old:
            entry = head
            while entry is not None:
                following = entry.next
                i = self._index(entry.hash)  # the stored hash saves hashing every key again
                entry.next = self._buckets[i]
                self._buckets[i] = entry
                entry = following
        self.resizes += 1

    def __contains__(self, key) -> bool:
        return self._find(key, self._hash(key)) is not None

    def __len__(self) -> int:
        return self._size

    def items(self) -> Iterator[tuple]:
        for head in self._buckets:
            entry = head
            while entry is not None:
                yield entry.key, entry.value
                entry = entry.next

    def keys(self) -> Iterator:
        for key, _ in self.items():
            yield key

    def stats(self) -> dict:
        """How full the map is and how long its chains are."""
        longest, used = 0, 0
        for head in self._buckets:
            length, entry = 0, head
            while entry is not None:
                length += 1
                entry = entry.next
            used += length > 0
            longest = max(longest, length)
        return {"size": self._size, "capacity": len(self._buckets), "load_factor": round(self._size / len(self._buckets), 3),
                "longest_chain": longest, "empty_buckets": len(self._buckets) - used, "resizes": self.resizes}

    def __repr__(self) -> str:
        return f"HashMap(size={self._size}, capacity={len(self._buckets)})"


# ── Binary search tree ────────────────────────────────────────────────

class _TreeNode:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree(SortedMapADT):
    """Every key in a node's left subtree is smaller than the node's key, every key in
    the right subtree is larger.

    The tree does not rebalance itself. Keys added in random order give a height of
    about 2 to 3 times log2(n); keys added already sorted give a chain of height n.

    | Operation | Average (random order) | Worst case (sorted input) |
    |---|---|---|
    | put, get, remove | O(log n) | O(n) |
    | in-order walk | O(n) | O(n) |
    | range(low, high) | O(log n + matches) | O(n) |
    """

    def __init__(self):
        self._root: Optional[_TreeNode] = None
        self._size = 0

    def put(self, key, value):
        if self._root is None:
            self._root = _TreeNode(key, value)
            self._size = 1
            return None
        node = self._root
        while True:
            if key < node.key:
                if node.left is None:
                    node.left = _TreeNode(key, value)
                    break
                node = node.left
            elif node.key < key:
                if node.right is None:
                    node.right = _TreeNode(key, value)
                    break
                node = node.right
            else:
                old, node.value = node.value, value
                return old
        self._size += 1
        return None

    def _node(self, key) -> Optional[_TreeNode]:
        node = self._root
        while node is not None:
            if key < node.key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                return node
        return None

    def get(self, key, default=None):
        node = self._node(key)
        return default if node is None else node.value

    def __contains__(self, key) -> bool:
        return self._node(key) is not None

    def remove(self, key):
        parent, node = None, self._root
        while node is not None and node.key != key:
            parent, node = node, (node.left if key < node.key else node.right)
        if node is None:
            return None
        removed = node.value

        if node.left is not None and node.right is not None:
            # Two children: copy the in-order successor (smallest key on the right) into
            # this node, then remove the successor, which has no left child.
            succ_parent, succ = node, node.right
            while succ.left is not None:
                succ_parent, succ = succ, succ.left
            node.key, node.value = succ.key, succ.value
            parent, node = succ_parent, succ

        child = node.left if node.left is not None else node.right  # zero or one child left
        if parent is None:
            self._root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child
        self._size -= 1
        return removed

    def min_key(self):
        if self._root is None:
            raise KeyError("min_key of an empty tree")
        node = self._root
        while node.left is not None:
            node = node.left
        return node.key

    def max_key(self):
        if self._root is None:
            raise KeyError("max_key of an empty tree")
        node = self._root
        while node.right is not None:
            node = node.right
        return node.key

    def items(self) -> Iterator[tuple]:
        """In-order walk with an explicit stack: the keys come out sorted."""
        stack, node = [], self._root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node.key, node.value
            node = node.right

    def keys(self) -> Iterator:
        for key, _ in self.items():
            yield key

    def range(self, low, high) -> Iterator[tuple]:
        """In-order walk that skips subtrees that lie fully outside [low, high)."""
        stack, node = [], self._root
        while stack or node is not None:
            while node is not None:
                if node.key < low:
                    node = node.right  # everything on the left is smaller still
                else:
                    stack.append(node)
                    node = node.left
            if not stack:
                return
            node = stack.pop()
            if not node.key < high:
                return
            yield node.key, node.value
            node = node.right

    def height(self) -> int:
        """Number of levels: 0 for an empty tree, 1 for a single node."""
        if self._root is None:
            return 0
        level, height = [self._root], 0
        while level:
            height += 1
            level = [child for n in level for child in (n.left, n.right) if child is not None]
        return height

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"BinarySearchTree(size={self._size})"
