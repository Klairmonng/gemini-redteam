# Acceptance test plan: Canary Lab analysis pipeline

| Item | Value |
|---|---|
| Test plan id | ATP-CANARY-01 |
| Version | 1.1 |
| Date | 2026-11-19 |
| Author | [Your name] |
| Status | Executed on 2026-11-19, retested after fixes the same day, see the [test report](test-report.md) |
| Approval of the project by the Testing teacher | [Pending] |

The chapters follow IEEE 829 [3]. A chapter that does not apply to this project says NA (not applicable) and why.

## 1. Introduction

This plan describes how Canary Lab is tested before its results are used in the Applied AI report and before it is shown in the Algorithmic Programming interview. Canary Lab scores Gemini answers for leaks of a made-up access code, combines that with LLM judge grades, and shows the results on a page. The [requirements](requirements.md) document describes the system, the stakeholders and 26 requirements.

The question this test answers: can the stakeholders rely on the levels, the data structures and the server, and if not, what has to be fixed first?

## 2. Test items

Table 1: Test items and their versions.

| Item | File | Version |
|---|---|---|
| Rule check | `deviation_detector.py` | As on 2026-11-19 (the project has no version control yet, see 15) |
| Judge panel logic | `llm_judge.py` | As on 2026-11-19 |
| Data structures and algorithms | `datalab/` | As on 2026-11-19 |
| Local server | `pipeline-app/serve.py` | As on 2026-11-19 |
| Page, Data section | `pipeline-app/index.html` | As on 2026-11-19 |

## 3. Features to be tested

All 26 requirements in the [requirements](requirements.md) document, tables 3 to 7: R-DET-1 to R-DET-6, R-JDG-1 to R-JDG-5, R-DS-1 to R-DS-4, R-ALG-1 to R-ALG-3, R-APP-1 to R-APP-5, R-SRV-1 to R-SRV-3 and R-PERF-1.

## 4. Features not to be tested

See [requirements](requirements.md) table 9: the live API calls, the attack content, the drift charts and the published replay copy.

## 5. Risk analysis

### 5.1 Method

A product risk analysis in the style of TMap Next [2]. For each requirement group: what can go wrong, how likely it is, and how much it would hurt each stakeholder from [requirements](requirements.md) table 2 (S1 researcher, S2 Applied AI assessor, S3 Algorithmic Programming teacher, S4 readers of the findings).

Likelihood and impact are scored 1 (low), 2 (medium) or 3 (high). Risk = likelihood × impact, where impact is the highest score over the stakeholders.

Table 2: Risk classes and what they mean for testing.

| Risk class | Risk score | Test depth |
|---|---|---|
| A | 6 to 9 | Thorough: at least two design techniques, every class and boundary, plus error guessing |
| B | 3 to 4 | Medium: one design technique over the main classes |
| C | 1 to 2 | Light: a few tests or a manual check |

### 5.2 Product risks

Table 3: Product risks, scored per stakeholder.

| Id | Requirements | What can go wrong | Likelihood and why | S1 | S2 | S3 | S4 | Score | Class |
|---|---|---|---|---|---|---|---|---|---|
| PR-01 | R-DET-1, R-DET-2 | A leak in a form the rules do not know scores 0 | 3: the attacks ask for encodings on purpose (base64, NATO, reversed), and each rule is a narrow string match | 3: attack success is undercounted | 3: claims rest on these counts | 1 | 3: a model looks safer than it is | 9 | A |
| PR-02 | R-DET-5 | A harmless answer scores 2 or 3 | 1: needs an answer that mentions Azure or a number with 7741 | 2 | 3: combine() keeps a rule level of 2 or 3 over the judges | 1 | 3: a model is said to leak when it did not | 3 | B |
| PR-03 | R-DET-3, R-DET-4, R-DET-6 | A leak in code output or an earlier turn is missed, or the attacker's own words count as a leak | 2: several channels and the attacker text make the logic longer | 3 | 3 | 1 | 3 | 6 | A |
| PR-04 | R-JDG-1, R-JDG-2, R-JDG-3 | The final level is combined wrongly | 1: small functions | 3: every final level depends on it | 3 | 1 | 3 | 3 | B |
| PR-05 | R-JDG-4, R-JDG-5 | A judge reply is read wrongly or lost | 2: LLM replies vary in format | 2: missing grades | 2 | 1 | 1 | 4 | B |
| PR-06 | R-DS-1 to R-DS-4 | A structure loses or corrupts records | 2: new, hand-written pointer code | 2 | 1 | 3: the interview is about this code | 1 | 6 | A |
| PR-07 | R-ALG-1 to R-ALG-3, R-APP-1 | A sort or search gives a wrong order or misses records | 2: new code with many edge cases (empty, duplicates, sorted input) | 2 | 1 | 3 | 1 | 6 | A |
| PR-08 | R-APP-2, R-APP-3, R-APP-5 | The page shows a wrong portion or time, or is hard to use | 1: thin layer over tested code | 1 | 1 | 2: visible in the demo | 1 | 2 | C |
| PR-09 | R-PERF-1, R-APP-4 | The demo hangs on the largest portion | 2: Python is slow and insertion sort is O(n²) | 1 | 1 | 2 | 1 | 4 | B |
| PR-10 | R-SRV-1 | Another website starts live runs with the saved API keys | 1: the server only listens on 127.0.0.1 | 3: quota and keys | 1 | 1 | 1 | 3 | B |
| PR-11 | R-SRV-2, R-SRV-3 | A bad request crashes the server or starts an unwanted run | 1 | 2 | 1 | 1 | 1 | 2 | C |

### 5.3 Project risks

Table 4: Risks to the test project itself.

| Id | Risk | Measure |
|---|---|---|
| PJ-01 | The teacher does not approve this project as the test subject | Ask for approval with this plan before the deadline in week 8 [1] |
| PJ-02 | Tests that call the APIs would use the daily quota (20 requests per model) | No test calls an API; the server tests only send requests the server must refuse |
| PJ-03 | Timing tests fail on a slower computer without a bug | Limits are set well above the measured times; the measured times are logged |
| PJ-04 | No version control, so a test result cannot be tied to a code version | Run the tests again before handing in; put the project in Git (see 15) |

## 6. Approach

### 6.1 Test levels

Table 5: Test levels.

| Level | What | How | Who |
|---|---|---|---|
| Unit test | Functions and classes on their own | Python unittest, automated | Researcher, with Claude Code |
| Integration test | The page's API through the real HTTP server, the join of answers and grades | Python unittest, a server on a free port inside the test | Researcher, with Claude Code |
| System and acceptance test | The page used as a user would | Manual test scripts MT-01 to MT-07 in [test case design](test-case-design.md) chapter 7 | Researcher |
| Performance test | Times at the largest portion | Python unittest with timers | Researcher |

### 6.2 Risk class, depth and techniques

Table 6: Which technique covers which risk.

| Risk | Class | Techniques | Test cases |
|---|---|---|---|
| PR-01 | A | Equivalence partitioning on the form of the code, error guessing on forms the rules may miss | TC-DET-01 to TC-DET-07, TC-DET-21, TC-DET-24 |
| PR-03 | A | Equivalence partitioning on levels, attacker text and channels; boundary value analysis on fragment length | TC-DET-08 to TC-DET-17 |
| PR-06 | A | State transition (list), decision table (tree removal), boundary value analysis (index, load factor, range), equivalence partitioning, error guessing (collisions, sorted input) | TC-IF, TC-DLL, TC-HM, TC-BST |
| PR-07 | A | Equivalence partitioning on input classes, boundary value analysis on search positions, decision table on the join, cross-checks against Python | TC-SORT, TC-BIN, TC-SEQ, TC-DS-01 to TC-DS-03 |
| PR-02 | B | Error guessing on look-alike answers | TC-DET-18 to TC-DET-20, TC-DET-22, TC-DET-23 |
| PR-04 | B | Decision table with all 20 combinations; boundary value analysis on the number of grades | TC-JDG-01 to TC-JDG-10 |
| PR-05 | B | Equivalence partitioning and boundary value analysis on judge replies | TC-JDG-11 to TC-JDG-17 |
| PR-09 | B | Performance test at the upper boundary; boundary value analysis on the insertion sort limit | TC-PERF-01 to TC-PERF-04, TC-LAB-06 |
| PR-10 | B | Equivalence partitioning on who sends the request | TC-SRV-07 to TC-SRV-11 |
| PR-08 | C | Manual test scripts; requests through the lab service | MT-01 to MT-07, TC-LAB-01 to TC-LAB-05, TC-DS-04 to TC-DS-08 |
| PR-11 | C | Equivalence partitioning and boundary value analysis on requests | TC-SRV-01 to TC-SRV-06, TC-SRV-12 to TC-SRV-17 |

The design of every test case is in [test case design](test-case-design.md).

### 6.3 Known issues in the automated tests

A test case states what the requirement asks for. When the system does not do it yet, the test is marked `@unittest.expectedFailure` and names its issue in the [issue register](issue-register.md). This keeps the issue visible in every run without hiding new failures: when the issue is fixed, unittest reports an unexpected success, and the marker is removed.

## 7. Item pass and fail criteria (acceptance criteria)

Table 7: Acceptance criteria.

| Id | Criterion |
|---|---|
| AC-1 | Every requirement has at least one test case |
| AC-2 | Every test case for a risk class A requirement passes, or its issue has priority P3 |
| AC-3 | No issue with priority P1 is open |
| AC-4 | The automated tests run with one command, without internet or API keys, and give the same result twice in a row |
| AC-5 | R-PERF-1 is met |
| AC-6 | Manual tests MT-01 to MT-07 pass |

The system is accepted when all six criteria are met. A part of the system can be accepted on its own when its criteria are met.

Table 8: Issue priorities.

| Priority | Meaning |
|---|---|
| P1 | Fix before the results are used in the report or the portfolio |
| P2 | Fix before the next round of data collection or the interview |
| P3 | Fix when convenient |

## 8. Suspension criteria and resumption requirements

Testing stops when the test suite cannot start (an import fails) or when a test changes the result files. It resumes when the cause is fixed and the full suite runs again from the start. No test writes to the result files; the dataset tests use a temporary folder.

## 9. Test deliverables

Table 9: Deliverables.

| Deliverable | File |
|---|---|
| Requirements | [requirements.md](requirements.md) |
| This plan | [acceptance-test-plan.md](acceptance-test-plan.md) |
| Test case design | [test-case-design.md](test-case-design.md) |
| Automated tests | [../tests/](../tests/) |
| Test runner | [run_tests.py](run_tests.py) |
| Test results, written by the runner | [test-results.md](test-results.md), [test-results.json](test-results.json) |
| Issue register | [issue-register.md](issue-register.md) |
| Test report | [test-report.md](test-report.md) |

## 10. Testing tasks

Table 10: Tasks in order.

| No. | Task | Result |
|---|---|---|
| 1 | Write requirements from the source documents | requirements.md |
| 2 | Risk analysis | Chapter 5 |
| 3 | Design test cases per technique | test-case-design.md |
| 4 | Build the automated tests and the runner | tests/, run_tests.py |
| 5 | Run the tests and the manual scripts, register issues | test-results.md, issue-register.md |
| 6 | Fix issues where agreed and run everything again | Updated results |
| 7 | Write the test report | test-report.md |

## 11. Environmental needs, and advice on the test system

### 11.1 Environment used

Table 11: Test environment.

| Item | Value |
|---|---|
| Computer | The student's laptop, Windows 10 |
| Python | 3.15.0, standard library only |
| Browser for manual tests | The browser pane of the Claude desktop app (Chromium based) |
| Data | The study's result files in the project folder (63 answers and 71 judge grades at the first run; 64 and 72 after one live run during testing); the dataset tests use their own small files |
| Network | None needed; the server tests use 127.0.0.1 on a free port |

### 11.2 Which system to use for the acceptance test

Table 12: Options for running the acceptance test.

| Option | For | Against |
|---|---|---|
| Python unittest with `testing/run_tests.py` | Part of Python, nothing to install, runs offline on any school computer, writes the results table for the report | Plain output; no browser tests |
| pytest with the pytest-html plugin | Shorter tests, ready HTML report | Must be installed; adds a dependency the teachers would also need |
| GitHub Actions running `run_tests.py` on every change | Each change is tested automatically, with a dated log per version, which fixes PJ-04 | Needs the project on GitHub; secrets must stay out of the repository |
| Manual test scripts for the page | No tools; matches how a user works | Slow, and depends on the tester following the steps |
| Playwright browser tests for the page | Repeatable page tests | New tool and set-up time for only seven page checks |

Advice: use unittest with `run_tests.py` for this round, because it runs anywhere without installing anything and its results table goes straight into the report. Keep the page checks as manual scripts while there are only seven. When the project goes into Git, add a GitHub Actions job that runs `python testing/run_tests.py`, so every version has its own test log. Playwright is worth it only if the page gets more interactive parts.

## 12. Responsibilities

Table 13: Roles.

| Role | Who |
|---|---|
| Test manager, test designer, tester | [Your name], with Claude Code as assistant |
| Approves the test project | The Testing teacher [1] |
| Decides on fixing issues | [Your name] |

## 13. Staffing and training needs

NA: a one-person project; the techniques come from the Testing module.

## 14. Schedule

Table 14: Schedule.

| Activity | Date |
|---|---|
| Requirements, risk analysis, test design | 2026-11-19 |
| First test run and issue registration | 2026-11-19 |
| Fix ISS-11 and run again | 2026-11-19 |
| Test report version 1.0 | 2026-11-19 |
| Fix ISS-01 to ISS-06, run again, report version 1.1 | 2026-11-19 |
| Hand-in deadline (week 8) | [Date] |

## 15. Risks and contingencies

See chapter 5. Contingency for PJ-04: until the project is in Git, run `python testing/run_tests.py` again on the day of hand-in, so the results file matches the handed-in code.

## 16. Approvals

Table 15: Approvals.

| Who | Decision | Date |
|---|---|---|
| Testing teacher | Approval of the project as test subject: [Pending] | [Date] |
| [Your name] | Plan approved for execution | 2026-11-19 |

## References

| No. | Source |
|---|---|
| [1] | NHL Stenden, Module book OIT Testing, version 7.2, 2021 |
| [2] | Koomen, van der Aalst, Broekman, Vroon, TMap Next, 2006 |
| [3] | IEEE 829-2008, Standard for Software and System Test Documentation |
| [4] | ISO/IEC 25010:2011, Systems and software quality models |
| [5] | [requirements.md](requirements.md) |
