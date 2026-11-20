# Testing

The test documents for the OIT Testing module. Read them in this order:

| No. | Document | What it holds |
|---|---|---|
| 1 | [requirements.md](requirements.md) | The system, its stakeholders and 26 requirements |
| 2 | [acceptance-test-plan.md](acceptance-test-plan.md) | Risk analysis, approach, acceptance criteria, advice on the test system |
| 3 | [test-case-design.md](test-case-design.md) | How each test case was derived, per technique, and the manual scripts |
| 4 | [issue-register.md](issue-register.md) | Every issue found, with priority and status |
| 5 | [test-report.md](test-report.md) | Results, findings and the verdict |
| | [test-results.md](test-results.md) | Written by the runner: every test case and its result |

Run all tests and write the results table again (from the `gemini-redteam` folder):

```
python testing/run_tests.py
```

Or only the tests, with unittest's own output:

```
python -m unittest discover -s tests -v
```

No test calls an API or needs the internet.
