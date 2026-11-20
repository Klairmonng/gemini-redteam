import random
import unittest

from datalab.algorithms import (SORTS, binary_search, binary_search_range, insertion_sort, is_sorted, lower_bound,
                                merge_sort, quick_sort, sequential_search, upper_bound)

STABLE = (merge_sort, insertion_sort)


def input_classes():
    """Equivalence classes of input for a sort, one representative each."""
    rng = random.Random(10)
    return {
        "empty": [],
        "one element": [7],
        "two in order": [1, 2],
        "two reversed": [2, 1],
        "three elements": [2, 3, 1],
        "already sorted": list(range(200)),
        "reversed": list(range(200, 0, -1)),
        "all equal": [5] * 100,
        "few distinct values (like levels 0-3)": [rng.randrange(4) for _ in range(500)],
        "random integers": [rng.randrange(-1000, 1000) for _ in range(500)],
        "floats": [rng.uniform(-1, 1) for _ in range(300)],
        "strings": [rng.choice(["gemini", "claude", "Auto", "", "unknown", "3.5 Flash-Lite"]) + str(rng.randrange(50))
                    for _ in range(300)],
        "organ pipe": list(range(100)) + list(range(100, 0, -1)),
    }


class TestSortCorrectness(unittest.TestCase):
    """[R-ALG-1] Technique: equivalence partitioning on the input. Every sort, in both directions,
    must give the same keys in the same order as Python's sorted()."""

    def test_TC_SORT_01_every_class_ascending(self):
        for name, data in input_classes().items():
            for sort_name, sort in SORTS.items():
                with self.subTest(sort=sort_name, input=name):
                    self.assertEqual(sort(data), sorted(data))

    def test_TC_SORT_02_every_class_descending(self):
        for name, data in input_classes().items():
            for sort_name, sort in SORTS.items():
                with self.subTest(sort=sort_name, input=name):
                    self.assertEqual(sort(data, reverse=True), sorted(data, reverse=True))

    def test_TC_SORT_03_input_is_not_changed(self):
        data = [3, 1, 2]
        for sort_name, sort in SORTS.items():
            with self.subTest(sort=sort_name):
                sort(data)
                self.assertEqual(data, [3, 1, 2])

    def test_TC_SORT_04_key_function_on_records(self):
        records = [{"id": i, "level": lvl} for i, lvl in enumerate([2, 0, 3, 1, 3, 0])]
        for sort_name, sort in SORTS.items():
            with self.subTest(sort=sort_name):
                result = sort(records, key=lambda r: r["level"])
                self.assertEqual([r["level"] for r in result], [0, 0, 1, 2, 3, 3])
                self.assertTrue(is_sorted(result, key=lambda r: r["level"]))

    def test_TC_SORT_05_random_cross_check(self):
        rng = random.Random(11)
        for _ in range(60):
            data = [rng.randrange(50) for _ in range(rng.randrange(0, 120))]
            for sort_name, sort in SORTS.items():
                self.assertEqual(sort(data), sorted(data), sort_name)


class TestSortStability(unittest.TestCase):
    """[R-ALG-2] Technique: equivalence partitioning on equal keys. Merge and insertion sort are
    stable: records with the same key keep their earlier order, in both directions,
    exactly as Python's sorted() does. Quick sort is not stable, so only its keys are checked."""

    def setUp(self):
        rng = random.Random(12)
        self.records = [{"id": i, "level": rng.randrange(4)} for i in range(400)]
        self.key = lambda r: r["level"]

    def test_TC_SORT_06_stable_sorts_keep_order_of_equal_keys(self):
        for sort in STABLE:
            for reverse in (False, True):
                with self.subTest(sort=sort.__name__, descending=reverse):
                    got = [r["id"] for r in sort(self.records, key=self.key, reverse=reverse)]
                    want = [r["id"] for r in sorted(self.records, key=self.key, reverse=reverse)]
                    self.assertEqual(got, want)

    def test_TC_SORT_07_quick_sort_keys_are_right(self):
        got = quick_sort(self.records, key=self.key)
        self.assertEqual([self.key(r) for r in got], sorted(self.key(r) for r in self.records))
        self.assertEqual(sorted(r["id"] for r in got), list(range(400)))  # nothing lost or doubled


class TestSortScale(unittest.TestCase):
    """[R-ALG-1] Technique: error guessing. Already sorted and reversed input are the classic
    worst case of a quick sort that splits on the first or last element; the median of
    three must avoid it. Done on 50,000 elements, which would not finish in time with
    an O(n^2) split."""

    def test_TC_SORT_08_quick_sort_on_large_sorted_and_reversed_input(self):
        for data in (list(range(50000)), list(range(50000, 0, -1)), [1] * 50000):
            self.assertEqual(quick_sort(data), sorted(data))

    def test_TC_SORT_09_merge_sort_on_size_not_a_power_of_two(self):
        for n in (31, 32, 33, 1000, 1023, 1025):
            data = list(range(n, 0, -1))
            self.assertEqual(merge_sort(data), sorted(data))


class TestBinarySearch(unittest.TestCase):
    """[R-ALG-3] Technique: boundary value analysis on the target's position in the sorted array:
    before the first element, on the first, inside, on the last, after the last, and
    in a gap between values."""

    def setUp(self):
        self.data = [10, 20, 20, 20, 30, 40, 50]

    def test_TC_BIN_01_target_before_first(self):
        self.assertEqual(binary_search(self.data, 5), [])
        self.assertEqual((lower_bound(self.data, 5), upper_bound(self.data, 5)), (0, 0))

    def test_TC_BIN_02_target_on_first(self):
        self.assertEqual(binary_search(self.data, 10), [10])

    def test_TC_BIN_03_run_of_equal_values(self):
        self.assertEqual(binary_search(self.data, 20), [20, 20, 20])
        self.assertEqual((lower_bound(self.data, 20), upper_bound(self.data, 20)), (1, 4))

    def test_TC_BIN_04_target_on_last(self):
        self.assertEqual(binary_search(self.data, 50), [50])

    def test_TC_BIN_05_target_after_last(self):
        self.assertEqual(binary_search(self.data, 60), [])
        self.assertEqual(lower_bound(self.data, 60), len(self.data))

    def test_TC_BIN_06_target_in_a_gap(self):
        self.assertEqual(binary_search(self.data, 25), [])
        self.assertEqual(lower_bound(self.data, 25), 4)

    def test_TC_BIN_07_empty_and_single_arrays(self):
        self.assertEqual(binary_search([], 1), [])
        self.assertEqual(binary_search([1], 1), [1])
        self.assertEqual(binary_search([1], 0), [])

    def test_TC_BIN_08_range_includes_both_ends(self):
        self.assertEqual(binary_search_range(self.data, 20, 40), [20, 20, 20, 30, 40])
        self.assertEqual(binary_search_range(self.data, 21, 29), [])

    def test_TC_BIN_09_records_by_key(self):
        records = merge_sort([{"m": m} for m in ["b", "a", "c", "a"]], key=lambda r: r["m"])
        self.assertEqual(len(binary_search(records, "a", key=lambda r: r["m"])), 2)

    def test_TC_BIN_10_agrees_with_sequential_search(self):
        rng = random.Random(13)
        data = sorted(rng.randrange(100) for _ in range(1000))
        for target in range(-5, 106):
            with self.subTest(target=target):
                self.assertEqual(binary_search(data, target), sequential_search(data, lambda x: x == target))


class TestSequentialSearch(unittest.TestCase):
    """[R-ALG-3] Technique: equivalence partitioning on the result: no match, some, all, and an
    empty collection. Works on any iterable, including the linked list."""

    def test_TC_SEQ_01_result_classes(self):
        data = ["leak AZURE-7741", "refused", "azure sky", "no"]
        has_azure = lambda s: "azure" in s.lower()  # noqa: E731
        self.assertEqual(sequential_search(data, lambda s: "xyz" in s), [])
        self.assertEqual(sequential_search(data, has_azure), ["leak AZURE-7741", "azure sky"])
        self.assertEqual(sequential_search(data, lambda s: True), data)
        self.assertEqual(sequential_search([], has_azure), [])

    def test_TC_SEQ_02_on_the_linked_list_keeps_list_order(self):
        from datalab.structures import DoublyLinkedList
        dll = DoublyLinkedList([5, 1, 5, 2, 5])
        self.assertEqual(sequential_search(dll, lambda x: x != 5), [1, 2])


if __name__ == "__main__":
    unittest.main()
