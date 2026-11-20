"""Three sorting algorithms and two searching algorithms, written by hand.

Every sort takes an array, a key function and a direction, and returns a new sorted
array; the input is left as it was. The keys are worked out once per element and kept
in a parallel array, so the key function is not called again on every comparison.

| Algorithm | Best | Average | Worst | Extra memory | Stable |
|---|---|---|---|---|---|
| Quick sort (Hoare, median of three) | O(n log n) | O(n log n) | O(n^2) | O(log n) stack | No |
| Merge sort (bottom-up) | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Insertion sort | O(n) | O(n^2) | O(n^2) | O(1) | Yes |
| Sequential search | O(1) | O(n) | O(n) | | |
| Binary search (needs sorted input) | O(1) | O(log n) | O(log n) | | |

Stable means records with equal keys keep the order they had before the sort.
"""

from typing import Callable, Iterable, List


def identity(x):
    return x


def _ordering(reverse: bool) -> Callable:
    """before(a, b) is True when a must come before b."""
    if reverse:
        return lambda a, b: b < a
    return lambda a, b: a < b


# ── Sorting ───────────────────────────────────────────────────────────

def quick_sort(array: List, key: Callable = identity, reverse: bool = False) -> List:
    items = list(array)
    keys = [key(x) for x in items]
    before = _ordering(reverse)

    def swap(i, j):
        keys[i], keys[j] = keys[j], keys[i]
        items[i], items[j] = items[j], items[i]

    def partition(lo, hi):
        # Median of three: order the first, middle and last keys, then split on the
        # middle one. This avoids the O(n^2) case for input that is already sorted.
        mid = (lo + hi) // 2
        if before(keys[mid], keys[lo]):
            swap(mid, lo)
        if before(keys[hi], keys[lo]):
            swap(hi, lo)
        if before(keys[hi], keys[mid]):
            swap(hi, mid)
        pivot = keys[mid]
        # Hoare partition: two indexes walk towards each other and swap pairs that are
        # on the wrong side. Equal keys stop both walks, so many duplicates (the levels
        # 0 to 3) still split evenly.
        i, j = lo - 1, hi + 1
        while True:
            i += 1
            while before(keys[i], pivot):
                i += 1
            j -= 1
            while before(pivot, keys[j]):
                j -= 1
            if i >= j:
                return j
            swap(i, j)

    stack = [(0, len(items) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        p = partition(lo, hi)
        # Push the larger part first so the smaller one is handled next: the stack never
        # holds more than about log2(n) ranges.
        left, right = (lo, p), (p + 1, hi)
        if p - lo > hi - p - 1:
            stack.append(left)
            stack.append(right)
        else:
            stack.append(right)
            stack.append(left)
    return items


def merge_sort(array: List, key: Callable = identity, reverse: bool = False) -> List:
    """Bottom-up: merge runs of 1, then 2, then 4 and so on, between two buffers."""
    n = len(array)
    src_items, src_keys = list(array), [key(x) for x in array]
    dst_items, dst_keys = [None] * n, [None] * n
    before = _ordering(reverse)
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid, hi = min(lo + width, n), min(lo + 2 * width, n)
            i, j, k = lo, mid, lo
            while i < mid and j < hi:
                # Take from the right run only when it is strictly before the left one:
                # that keeps equal keys in their old order (stable).
                if before(src_keys[j], src_keys[i]):
                    dst_items[k], dst_keys[k] = src_items[j], src_keys[j]
                    j += 1
                else:
                    dst_items[k], dst_keys[k] = src_items[i], src_keys[i]
                    i += 1
                k += 1
            while i < mid:
                dst_items[k], dst_keys[k] = src_items[i], src_keys[i]
                i += 1
                k += 1
            while j < hi:
                dst_items[k], dst_keys[k] = src_items[j], src_keys[j]
                j += 1
                k += 1
        src_items, dst_items = dst_items, src_items
        src_keys, dst_keys = dst_keys, src_keys
        width *= 2
    return src_items


def insertion_sort(array: List, key: Callable = identity, reverse: bool = False) -> List:
    items = list(array)
    keys = [key(x) for x in items]
    before = _ordering(reverse)
    for i in range(1, len(items)):
        item, k = items[i], keys[i]
        j = i - 1
        while j >= 0 and before(k, keys[j]):
            items[j + 1], keys[j + 1] = items[j], keys[j]
            j -= 1
        items[j + 1], keys[j + 1] = item, k
    return items


SORTS = {"quick": quick_sort, "merge": merge_sort, "insertion": insertion_sort}


def is_sorted(array: List, key: Callable = identity, reverse: bool = False) -> bool:
    before = _ordering(reverse)
    return all(not before(key(array[i + 1]), key(array[i])) for i in range(len(array) - 1))


# ── Searching ─────────────────────────────────────────────────────────

def sequential_search(elements: Iterable, predicate: Callable) -> List:
    """Look at every element in turn and keep the ones the predicate accepts."""
    return [e for e in elements if predicate(e)]


def lower_bound(array: List, target, key: Callable = identity) -> int:
    """First index whose key is not smaller than the target. The array must be sorted
    ascending by the same key."""
    lo, hi = 0, len(array)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(array[mid]) < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(array: List, target, key: Callable = identity) -> int:
    """First index whose key is larger than the target."""
    lo, hi = 0, len(array)
    while lo < hi:
        mid = (lo + hi) // 2
        if target < key(array[mid]):
            hi = mid
        else:
            lo = mid + 1
    return lo


def binary_search(array: List, target, key: Callable = identity) -> List:
    """Every element whose key equals the target, found by halving the search range.

    Two binary searches find where the run of equal keys starts and ends, so a target
    that matches 10,000 records costs the same O(log n) probes as one that matches one.
    """
    return array[lower_bound(array, target, key):upper_bound(array, target, key)]


def binary_search_range(array: List, low, high, key: Callable = identity) -> List:
    """Every element with low <= key <= high."""
    return array[lower_bound(array, low, key):upper_bound(array, high, key)]


SEARCHES = {"sequential": sequential_search, "binary": binary_search}
