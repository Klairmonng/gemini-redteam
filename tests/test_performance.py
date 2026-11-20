"""Time behaviour on the largest portion the page allows, requirement R-PERF-1.

The limits are wall-clock seconds on the computer that runs the tests, so a much slower
computer could fail them without a bug. The measured times go into the test log.
"""

import time
import unittest

from datalab import algorithms
from datalab.dataset import MAX_SCALE, Structures, load_records, take_portion
from datalab.lab import INSERTION_LIMIT

LIMIT_SECONDS = 5.0


class TestTimeBehaviour(unittest.TestCase):
    """[R-PERF-1] Technique: performance test at the upper boundary of the data size
    (MAX_SCALE copies) and at the insertion sort limit."""

    @classmethod
    def setUpClass(cls):
        records = load_records()
        if not records:
            raise unittest.SkipTest("no result files in the project folder")
        cls.portion = take_portion(records, scale=MAX_SCALE)
        start = time.perf_counter()
        cls.structures = Structures(cls.portion)
        cls.build_seconds = time.perf_counter() - start

    def timed(self, label, call):
        start = time.perf_counter()
        result = call()
        seconds = time.perf_counter() - start
        print(f"\n    {label}: {seconds:.2f} s", end="")
        return result, seconds

    def test_TC_PERF_01_build_all_three_structures(self):
        print(f"\n    build {len(self.portion):,} records: {self.build_seconds:.2f} s", end="")
        self.assertLess(self.build_seconds, LIMIT_SECONDS)

    def test_TC_PERF_02_quick_and_merge_sort(self):
        array = self.structures.linked.to_array()
        for name in ("quick", "merge"):
            for key in ("final", "text_length", "id"):
                with self.subTest(sort=name, key=key):
                    _, seconds = self.timed(f"{name} sort by {key}", lambda: algorithms.SORTS[name](array, key=lambda r: r[key]))
                    self.assertLess(seconds, LIMIT_SECONDS)

    def test_TC_PERF_03_insertion_sort_at_its_limit(self):
        array = self.structures.linked.to_array()[:INSERTION_LIMIT]
        _, seconds = self.timed(f"insertion sort of {len(array):,}", lambda: algorithms.insertion_sort(array, key=lambda r: r["text_length"]))
        self.assertLess(seconds, LIMIT_SECONDS)  # failed at 20,000 (8.9 s, ISS-11) and at 10,000 on battery (8.3 s, ISS-13)

    def test_TC_PERF_04_lookups_are_fast(self):
        some_id = self.portion[len(self.portion) // 2]["id"]
        _, hash_seconds = self.timed("hash map lookup", lambda: self.structures.by_id.get(some_id))
        _, tree_seconds = self.timed("tree range 200-400", lambda: list(self.structures.by_length.range((200, ""), (401, ""))))
        self.assertLess(hash_seconds, 0.01)
        self.assertLess(tree_seconds, 1.0)


if __name__ == "__main__":
    unittest.main()
