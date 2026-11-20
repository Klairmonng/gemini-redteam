"""Turns the study's result files into records and loads them into the three structures.

One record is one model answer, joined with the judges' grades for it:

| Field | Meaning |
|---|---|
| id | The answer's id (with `#0001`, `#0002` ... on scaled copies) |
| model, technique, goal, condition | What was attacked and how |
| text_length | Characters in the answer |
| rule_level | Level 0 to 3 from the canary rule check |
| panel | Combined judge level, or -1 when no judge graded it |
| final | The level the study reports (rule check and judges combined) |
| judges | How many grades were joined to it |
| judge_seconds | Time the judges took in total |
| timestamp | When the answer was recorded (empty for the hand-collected samples) |

The join uses the project's own HashMap: grades are put in a map from answer id to a
DoublyLinkedList of grades, then each answer looks up its list.
"""

import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import llm_judge  # noqa: E402  (the rule check, the id format and how levels combine)

from .structures import BinarySearchTree, DoublyLinkedList, HashMap  # noqa: E402

DATA_PAIRS = [
    ("sample_responses.jsonl", "judgments.jsonl"),
    ("responses_l4.jsonl", "judgments_l4.jsonl"),
    ("responses_generated.jsonl", "judgments_generated.jsonl"),
]
MAX_SCALE = 2000


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def make_record(row, grades, source):
    """One flat record from a response row and the DoublyLinkedList of its grades."""
    latest = HashMap()  # (judge, repeat) -> grade, the newest grade wins like in llm_judge
    for grade in grades:
        if "level" in grade:
            latest.put((grade["judge"], grade.get("repeat", 1)), grade)
    per_judge = HashMap()  # judge -> list of levels over repeats
    seconds = 0.0
    for (judge, _), grade in latest.items():
        levels = per_judge.get(judge)
        if levels is None:
            levels = []
            per_judge.put(judge, levels)
        levels.append(grade["level"])
        seconds += grade.get("seconds") or 0.0
    judge_levels = [llm_judge.upper_median(levels) for _, levels in per_judge.items()]
    panel = llm_judge.upper_median(judge_levels) if judge_levels else None
    rule = llm_judge.DETECTOR.score_response(row)["scored_level"]
    text = row.get("text") or ""
    return {
        "id": llm_judge.item_id(row),
        "source": source,
        "model": row.get("model") or "",
        "technique": row.get("technique") or row.get("attempt") or "",
        "goal": row.get("goal") or "canary",
        "condition": row.get("condition") or "",
        "prompt": row.get("prompt") or "",
        "text": text,
        "text_length": len(text),
        "rule_level": rule,
        "panel": -1 if panel is None else panel,
        "final": llm_judge.combine(rule, panel),
        "judges": len(latest),
        "judge_seconds": round(seconds, 2),
        "timestamp": row.get("timestamp") or "",
    }


def load_records(root=ROOT, pairs=DATA_PAIRS):
    """All answers in the project files, each joined with its grades, in file order."""
    records = []
    for responses_name, judgments_name in pairs:
        responses_path, judgments_path = Path(root) / responses_name, Path(root) / judgments_name
        if not responses_path.exists():
            continue
        grades_by_item = HashMap()
        if judgments_path.exists():
            for grade in read_jsonl(judgments_path):
                bucket = grades_by_item.get(grade["item"])
                if bucket is None:
                    bucket = DoublyLinkedList()
                    grades_by_item.put(grade["item"], bucket)
                bucket.add_last(grade)
        source = responses_path.stem
        for row in read_jsonl(responses_path):
            grades = grades_by_item.get(llm_judge.item_id(row)) or DoublyLinkedList()
            records.append(make_record(row, grades, source))
    return records


def take_portion(records, model="", limit=0, scale=1, seed=7):
    """The part of the data to work on.

    model: keep only this model's answers ("" keeps all).
    scale: make this many copies of every record, so timings are large enough to read.
        Copies get `#0001`, `#0002` ... after their id, and the scaled set is shuffled
        with a fixed seed. Without the shuffle each record's copies would arrive in key
        order and turn the tree into long chains (its O(n) worst case).
    limit: keep only the first this many records (0 keeps all).
    """
    if not (isinstance(scale, int) and 1 <= scale <= MAX_SCALE):
        raise ValueError(f"scale must be a whole number from 1 to {MAX_SCALE}")
    if not (isinstance(limit, int) and limit >= 0):
        raise ValueError("limit must be a whole number, 0 for all")
    chosen = [r for r in records if not model or r["model"] == model]
    if scale > 1:
        chosen = [{**r, "id": f"{r['id']}#{k:04d}", "copy": k} for k in range(1, scale + 1) for r in chosen]
        random.Random(seed).shuffle(chosen)
    return chosen[:limit] if limit else chosen


def tree_key(record):
    """The tree orders records by answer length; the id breaks ties so every key is unique."""
    return (record["text_length"], record["id"])


class Structures:
    """The records loaded into all three structures, with how long each took."""

    def __init__(self, records):
        self.timings = {}

        start = time.perf_counter()
        self.linked = DoublyLinkedList()
        for record in records:
            self.linked.add_last(record)
        self.timings["linked_list"] = time.perf_counter() - start

        start = time.perf_counter()
        self.by_id = HashMap()
        for record in records:
            self.by_id.put(record["id"], record)
        self.timings["hash_map"] = time.perf_counter() - start

        start = time.perf_counter()
        self.by_length = BinarySearchTree()
        for record in records:
            self.by_length.put(tree_key(record), record)
        self.timings["tree"] = time.perf_counter() - start

    def __len__(self):
        return len(self.linked)
