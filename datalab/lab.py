"""What the Data structures section of Canary Lab calls, through serve.py.

Three steps, each timed:

| Step | Request | Uses |
|---|---|---|
| Build | `{"action": "build", "scale": 100, "model": "", "limit": 0}` | All three structures |
| Sort | `{"action": "sort", "algorithm": "quick", "key": "final", "descending": true}` | The linked list's records as an array |
| Search | `{"action": "search", "algorithm": "binary", "field": "model", "query": "..."}` | List, array, map or tree |

After every sort or search the result is checked against Python's own `sorted()` or a
full scan, so the page can show that the hand-written code gives the right answer.
The check is not part of the timing.
"""

import threading
import time

from . import algorithms
from .dataset import MAX_SCALE, Structures, load_records, take_portion, tree_key

# Insertion sort is O(n^2). 20,000 records took 8.9 s (issue ISS-11), 10,000 take about 2 s,
# and 126,000 would take minutes.
INSERTION_LIMIT = 10000
PREVIEW_ROWS = 25
PREVIEW_FIELDS = ("id", "model", "technique", "final", "rule_level", "panel", "text_length", "judge_seconds", "timestamp")

SORT_KEYS = {
    "final": "Final level",
    "rule_level": "Rule check level",
    "panel": "Judge panel level",
    "text_length": "Answer length",
    "judge_seconds": "Judge time",
    "timestamp": "Recorded at",
    "model": "Model",
    "id": "Id",
}
TEXT_FIELDS = {"text": "Answer text", "prompt": "Attack prompt", "technique": "Technique", "model": "Model", "id": "Id"}
EXACT_FIELDS = {"final": int, "rule_level": int, "panel": int, "text_length": int, "model": str, "technique": str, "id": str}
SEARCH_ALGORITHMS = ("sequential", "binary", "hash", "tree")


def field_key(name):
    return lambda record: record[name]


def preview(records):
    return [{f: r.get(f) for f in PREVIEW_FIELDS} for r in records[:PREVIEW_ROWS]]


def same_records(a, b):
    """True when both hold the same records, in any order."""
    return len(a) == len(b) and sorted(r["id"] for r in a) == sorted(r["id"] for r in b)


class DataLab:
    def __init__(self, root=None):
        self.root = root
        self.lock = threading.Lock()
        self.records = None  # everything in the project files, loaded once
        self.structures = None
        self.portion = None

    def options(self):
        """What the page needs to draw its controls."""
        records = self._all()
        return {"models": sorted({r["model"] for r in records if r["model"]}), "records": len(records),
                "max_scale": MAX_SCALE, "insertion_limit": INSERTION_LIMIT, "sort_keys": SORT_KEYS,
                "text_fields": TEXT_FIELDS, "exact_fields": list(EXACT_FIELDS)}

    def _all(self):
        if self.records is None:
            self.records = load_records(self.root) if self.root else load_records()
        return self.records

    def handle(self, body):
        if not isinstance(body, dict):
            raise ValueError("send a JSON object")
        action = body.get("action")
        with self.lock:
            if action == "options":
                return self.options()
            if action == "build":
                return self.build(body.get("scale", 1), body.get("model", ""), body.get("limit", 0))
            if self.structures is None:
                raise ValueError("build the structures first")
            if action == "sort":
                return self.sort(body.get("algorithm"), body.get("key"), bool(body.get("descending")))
            if action == "search":
                return self.search(body.get("algorithm"), body.get("field"), body.get("query", ""))
        raise ValueError(f"unknown action {action!r}")

    # ── Steps ─────────────────────────────────────────────────────────

    def build(self, scale, model, limit):
        records = self._all()
        if model and model not in {r["model"] for r in records}:
            raise ValueError(f"no answers from model {model!r}")
        portion = take_portion(records, model=model, limit=limit, scale=scale)
        if not portion:
            raise ValueError("that portion has no records")
        self.structures = Structures(portion)
        self.portion = {"scale": scale, "model": model, "limit": limit}
        s = self.structures
        return {
            "action": "build", "records": len(s), "source_records": len(records), "portion": self.portion,
            "sample_id": s.linked.first()["id"],
            "timings": s.timings,
            "linked_list": {"size": len(s.linked)},
            "hash_map": s.by_id.stats(),
            "tree": {"size": len(s.by_length), "height": s.by_length.height(),
                     "shortest": s.by_length.min_key()[0], "longest": s.by_length.max_key()[0]},
        }

    def sort(self, algorithm, key, descending):
        if algorithm not in algorithms.SORTS:
            raise ValueError(f"unknown sort {algorithm!r}")
        if key not in SORT_KEYS:
            raise ValueError(f"unknown sort key {key!r}")
        array = self.structures.linked.to_array()
        if algorithm == "insertion" and len(array) > INSERTION_LIMIT:
            raise ValueError(f"insertion sort is O(n²), so it is limited to {INSERTION_LIMIT:,} records here "
                             f"({len(array):,} are loaded). Build a smaller portion, or pick quick or merge sort.")
        get = field_key(key)
        start = time.perf_counter()
        result = algorithms.SORTS[algorithm](array, key=get, reverse=descending)
        seconds = time.perf_counter() - start

        expected = sorted(array, key=get, reverse=descending)  # Python's built-in, stable sort
        same_keys = [get(r) for r in result] == [get(r) for r in expected]
        same_order = [r["id"] for r in result] == [r["id"] for r in expected]
        stable = algorithm != "quick"
        return {
            "action": "sort", "algorithm": algorithm, "key": key, "descending": descending, "records": len(result),
            "seconds": seconds, "preview": preview(result),
            "check": {"correct": same_keys and (same_order or not stable), "same_keys": same_keys,
                      "same_order": same_order, "stable_algorithm": stable,
                      "against": "Python's sorted()"},
        }

    def search(self, algorithm, field, query):
        if algorithm not in SEARCH_ALGORITHMS:
            raise ValueError(f"unknown search {algorithm!r}")
        s = self.structures
        query = str(query).strip()
        prep, prep_seconds = None, 0.0

        if algorithm == "sequential":
            if field not in TEXT_FIELDS:
                raise ValueError(f"sequential search looks inside a text field, not {field!r}")
            needle = query.lower()
            match = lambda r: needle in str(r[field]).lower()  # noqa: E731
            start = time.perf_counter()
            found = algorithms.sequential_search(s.linked, match)
            seconds = time.perf_counter() - start
            where = "the linked list, checking every record"

        elif algorithm == "binary":
            if field not in EXACT_FIELDS:
                raise ValueError(f"binary search needs an exact field, not {field!r}")
            target = self._parse(field, query)
            get = field_key(field)
            match = lambda r: r[field] == target  # noqa: E731
            start = time.perf_counter()
            array = algorithms.merge_sort(s.linked.to_array(), key=get)
            prep_seconds = time.perf_counter() - start
            prep = f"a merge sort by {field}, because binary search needs sorted input"
            start = time.perf_counter()
            found = algorithms.binary_search(array, target, key=get)
            seconds = time.perf_counter() - start
            where = "the array sorted by " + field

        elif algorithm == "hash":
            match = lambda r: r["id"] == query  # noqa: E731
            start = time.perf_counter()
            hit = s.by_id.get(query)
            seconds = time.perf_counter() - start
            found = [hit] if hit is not None else []
            where = "the hash map, by id"

        else:  # tree: answers whose length is in a range, written "200-400" or "300"
            low, high = self._length_range(query)
            match = lambda r: low <= r["text_length"] <= high  # noqa: E731
            start = time.perf_counter()
            found = [r for _, r in s.by_length.range((low, ""), (high + 1, ""))]
            seconds = time.perf_counter() - start
            where = "the binary search tree, by answer length"

        expected = [r for r in s.linked if match(r)]  # full scan with Python's own loop, for the check
        if algorithm == "tree":
            found_sorted = [tree_key(r) for r in found] == sorted(tree_key(r) for r in found)
        else:
            found_sorted = True
        return {
            "action": "search", "algorithm": algorithm, "field": "id" if algorithm == "hash" else field,
            "query": query, "where": where, "matches": len(found), "seconds": seconds,
            "prep": prep, "prep_seconds": prep_seconds, "preview": preview(found),
            "check": {"correct": same_records(found, expected) and found_sorted, "expected": len(expected),
                      "against": "a full scan of every record"},
        }

    @staticmethod
    def _parse(field, query):
        if EXACT_FIELDS[field] is int:
            try:
                return int(query)
            except ValueError:
                raise ValueError(f"{field} is a whole number, got {query!r}") from None
        return query

    @staticmethod
    def _length_range(query):
        parts = [p.strip() for p in query.replace("–", "-").split("-")]
        try:
            numbers = [int(p) for p in parts if p != ""]
        except ValueError:
            raise ValueError("write a length like 300 or a range like 200-400") from None
        if len(numbers) == 1 and len(parts) == 1:
            return numbers[0], numbers[0]
        if len(numbers) != 2 or numbers[0] > numbers[1] or numbers[0] < 0:
            raise ValueError("write a length like 300 or a range like 200-400, low first")
        return numbers[0], numbers[1]
