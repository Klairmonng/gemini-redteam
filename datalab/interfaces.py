"""The interfaces (abstract data types) the three data structures implement.

Python has no `interface` keyword like Java. An abstract base class does the same job:
a class that names the methods, and every structure that inherits from it must
implement all of them or Python refuses to create it.
"""

from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterator, Optional, TypeVar

E = TypeVar("E")  # element
K = TypeVar("K")  # key
V = TypeVar("V")  # value


class ListADT(ABC, Generic[E]):
    """An ordered list of elements that can grow and shrink at both ends."""

    @abstractmethod
    def add_first(self, element: E) -> None: ...

    @abstractmethod
    def add_last(self, element: E) -> None: ...

    @abstractmethod
    def remove_first(self) -> E: ...

    @abstractmethod
    def remove_last(self) -> E: ...

    @abstractmethod
    def first(self) -> E: ...

    @abstractmethod
    def last(self) -> E: ...

    @abstractmethod
    def get(self, index: int) -> E: ...

    @abstractmethod
    def remove_if(self, predicate: Callable[[E], bool]) -> int:
        """Remove every element the predicate accepts and return how many went."""

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __iter__(self) -> Iterator[E]: ...

    def is_empty(self) -> bool:
        return len(self) == 0


class MapADT(ABC, Generic[K, V]):
    """A collection of key and value pairs where each key appears once."""

    @abstractmethod
    def put(self, key: K, value: V) -> Optional[V]:
        """Store the value under the key. Returns the old value, or None if the key was new."""

    @abstractmethod
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]: ...

    @abstractmethod
    def remove(self, key: K) -> Optional[V]:
        """Delete the key. Returns its value, or None if the key was not there."""

    @abstractmethod
    def __contains__(self, key: K) -> bool: ...

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def keys(self) -> Iterator[K]: ...

    @abstractmethod
    def items(self) -> Iterator[tuple]: ...

    def values(self) -> Iterator[V]:
        for _, value in self.items():
            yield value

    def is_empty(self) -> bool:
        return len(self) == 0


class SortedMapADT(MapADT[K, V]):
    """A map that keeps its keys in order, so it can walk them sorted and answer range questions."""

    @abstractmethod
    def min_key(self) -> K: ...

    @abstractmethod
    def max_key(self) -> K: ...

    @abstractmethod
    def range(self, low: K, high: K) -> Iterator[tuple]:
        """Pairs with low <= key < high, in key order."""
