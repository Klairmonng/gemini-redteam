"""Run every unit test and write the results as a table for the test report.

    python testing/run_tests.py

Writes testing/test-results.md (for people) and testing/test-results.json (for tools).
Exits with 1 when a test fails, errors, or a known issue unexpectedly passes, so it can
also run in a CI pipeline. No test calls an API or needs the internet.
"""

import json
import platform
import re
import sys
import time
import unittest
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

TECHNIQUES = [
    ("equivalence partitioning", "Equivalence partitioning"),
    ("boundary value", "Boundary value analysis"),
    ("decision table", "Decision table"),
    ("state transition", "State transition"),
    ("error guessing", "Error guessing"),
    ("performance test", "Performance test"),
    ("checklist", "Checklist"),
]
OUTCOME_WORDS = {"pass": "Pass", "known": "Fail, known issue", "fail": "FAIL", "error": "ERROR",
                 "skip": "Skipped", "unexpected": "Passed, but marked as a known issue"}


class Recorder(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self.rows = []
        self._start = {}
        self._outcome = {}
        self._detail = {}

    def startTest(self, test):
        super().startTest(test)
        self._start[test.id()] = time.perf_counter()
        self._outcome[test.id()] = "pass"

    def _set(self, test, outcome, detail=""):
        self._outcome[test.id()] = outcome
        if detail:
            self._detail[test.id()] = detail

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._set(test, "fail", str(err[1]).splitlines()[0][:200])

    def addError(self, test, err):
        super().addError(test, err)
        self._set(test, "error", f"{err[0].__name__}: {str(err[1]).splitlines()[0][:200] if str(err[1]) else ''}")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            failed = issubclass(err[0], test.failureException)
            self._set(test, "fail" if failed else "error", f"{subtest._subDescription()}: {str(err[1]).splitlines()[0][:160]}")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._set(test, "skip", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._set(test, "known", str(err[1]).splitlines()[0][:200])

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._set(test, "unexpected")

    def stopTest(self, test):
        super().stopTest(test)
        tid = test.id()
        method = getattr(test, test._testMethodName, None)
        cls_doc = type(test).__doc__ or ""
        meth_doc = (method.__doc__ if method else "") or ""
        name = test._testMethodName
        m = re.match(r"test_(TC_[A-Z]+_\d+)_?(.*)", name)
        # A test's own "Technique:" line wins over its class's.
        source = meth_doc if "Technique:" in meth_doc else cls_doc
        technique_text = source.split("Technique:", 1)[-1].lower() if "Technique:" in source else ""
        self.rows.append({
            "id": m.group(1).replace("_", "-") if m else name,
            "title": (m.group(2) if m else name).replace("_", " "),
            "file": tid.split(".")[-3] + ".py" if tid.count(".") >= 2 else "",
            "class": type(test).__name__,
            "techniques": [label for key, label in TECHNIQUES if key in technique_text],
            # A test's own docstring can name its requirement; otherwise its class's apply.
            "requirements": sorted(set(re.findall(r"R-[A-Z]+-\d+", meth_doc) or re.findall(r"R-[A-Z]+-\d+", cls_doc))),
            "issue": ", ".join(sorted(set(re.findall(r"ISS-\d+", meth_doc)))),
            "outcome": self._outcome.get(tid, "pass"),
            "detail": self._detail.get(tid, ""),
            "seconds": round(time.perf_counter() - self._start.get(tid, time.perf_counter()), 3),
        })


def md_table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in rows]
    return "\n".join(lines)


def write_report(rows, started, seconds):
    counts = Counter(r["outcome"] for r in rows)
    by_req = defaultdict(Counter)
    by_tech = defaultdict(Counter)
    for r in rows:
        for req in r["requirements"] or ["(none)"]:
            by_req[req][r["outcome"]] += 1
        for tech in r["techniques"] or ["(none)"]:
            by_tech[tech][r["outcome"]] += 1

    def req_order(req):
        prefix, num = (req.rsplit("-", 1) + ["0"])[:2]
        order = ["R-DET", "R-JDG", "R-DS", "R-ALG", "R-APP", "R-SRV", "R-PERF"]
        return (order.index(prefix) if prefix in order else 99, int(num) if num.isdigit() else 0)

    out = [
        "# Test results",
        "",
        "Written by `python testing/run_tests.py`. Do not edit by hand: run it again instead.",
        "",
        md_table(["Item", "Value"], [
            ["Run at", started.strftime("%Y-%m-%d %H:%M")],
            ["Computer", platform.platform()],
            ["Python", platform.python_version()],
            ["Test cases", len(rows)],
            ["Duration", f"{seconds:.1f} s"],
        ]),
        "",
        "## Summary",
        "",
        md_table(["Result", "Test cases"], [[OUTCOME_WORDS[k], counts[k]] for k in OUTCOME_WORDS if counts[k]]),
        "",
        "A known issue is a test that describes what a requirement asks for and fails on purpose until the issue in the issue register is fixed.",
        "",
        "## By requirement",
        "",
        md_table(["Requirement", "Test cases", "Pass", "Known issue", "Fail or error"],
                 [[req, sum(c.values()), c["pass"], c["known"], c["fail"] + c["error"] + c["unexpected"]]
                  for req, c in sorted(by_req.items(), key=lambda kv: req_order(kv[0]))]),
        "",
        "## By test design technique",
        "",
        md_table(["Technique", "Test cases", "Pass", "Known issue", "Fail or error"],
                 [[t, sum(c.values()), c["pass"], c["known"], c["fail"] + c["error"] + c["unexpected"]]
                  for t, c in sorted(by_tech.items())]),
        "",
        "## Every test case",
        "",
        md_table(["Id", "Test case", "File", "Technique", "Requirement", "Result", "Issue", "Time"],
                 [[r["id"], r["title"], r["file"], ", ".join(r["techniques"]), ", ".join(r["requirements"]),
                   OUTCOME_WORDS[r["outcome"]], r["issue"], f"{r['seconds']:.2f} s"] for r in rows]),
        "",
    ]
    problems = [r for r in rows if r["outcome"] in ("fail", "error", "unexpected", "known")]
    if problems:
        out += ["## What the failing tests saw", "",
                md_table(["Id", "Result", "Message"], [[r["id"], OUTCOME_WORDS[r["outcome"]], r["detail"] or "(none)"] for r in problems]), ""]
    (HERE / "test-results.md").write_text("\n".join(out), encoding="utf-8")
    (HERE / "test-results.json").write_text(json.dumps({"run_at": started.isoformat(timespec="seconds"),
                                                         "python": platform.python_version(), "rows": rows}, indent=1), encoding="utf-8")


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    started = datetime.now()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    result = Recorder()
    start = time.perf_counter()
    suite.run(result)
    seconds = time.perf_counter() - start
    rows = sorted(result.rows, key=lambda r: (r["file"], r["id"]))
    write_report(rows, started, seconds)
    counts = Counter(r["outcome"] for r in rows)
    print(f"\n{len(rows)} test cases in {seconds:.1f} s: " + ", ".join(f"{OUTCOME_WORDS[k].lower()} {counts[k]}" for k in OUTCOME_WORDS if counts[k]))
    print(f"Results written to {HERE / 'test-results.md'}")
    bad = counts["fail"] + counts["error"] + counts["unexpected"]
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
