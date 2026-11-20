# Test results

Written by `python testing/run_tests.py`. Do not edit by hand: run it again instead.

| Item | Value |
|---|---|
| Run at | 2026-11-20 16:51 |
| Computer | Windows-10-10.0.19045-SP0 |
| Python | 3.13.7 |
| Test cases | 144 |
| Duration | 13.3 s |

## Summary

| Result | Test cases |
|---|---|
| Pass | 139 |
| Fail, known issue | 5 |

A known issue is a test that describes what a requirement asks for and fails on purpose until the issue in the issue register is fixed.

## By requirement

| Requirement | Test cases | Pass | Known issue | Fail or error |
|---|---|---|---|---|
| R-DET-1 | 3 | 3 | 0 | 0 |
| R-DET-2 | 8 | 8 | 0 | 0 |
| R-DET-3 | 5 | 5 | 0 | 0 |
| R-DET-4 | 3 | 3 | 0 | 0 |
| R-DET-5 | 5 | 4 | 1 | 0 |
| R-DET-6 | 3 | 3 | 0 | 0 |
| R-JDG-1 | 2 | 2 | 0 | 0 |
| R-JDG-2 | 2 | 2 | 0 | 0 |
| R-JDG-3 | 6 | 6 | 0 | 0 |
| R-JDG-4 | 5 | 4 | 1 | 0 |
| R-JDG-5 | 2 | 2 | 0 | 0 |
| R-DS-1 | 2 | 2 | 0 | 0 |
| R-DS-2 | 11 | 11 | 0 | 0 |
| R-DS-3 | 13 | 13 | 0 | 0 |
| R-DS-4 | 20 | 20 | 0 | 0 |
| R-ALG-1 | 7 | 7 | 0 | 0 |
| R-ALG-2 | 2 | 2 | 0 | 0 |
| R-ALG-3 | 12 | 12 | 0 | 0 |
| R-APP-1 | 4 | 4 | 0 | 0 |
| R-APP-2 | 6 | 5 | 1 | 0 |
| R-APP-3 | 5 | 5 | 0 | 0 |
| R-APP-4 | 1 | 1 | 0 | 0 |
| R-SRV-1 | 5 | 5 | 0 | 0 |
| R-SRV-2 | 6 | 5 | 1 | 0 |
| R-SRV-3 | 5 | 4 | 1 | 0 |
| R-PERF-1 | 4 | 4 | 0 | 0 |

## By test design technique

| Technique | Test cases | Pass | Known issue | Fail or error |
|---|---|---|---|---|
| Boundary value analysis | 49 | 46 | 3 | 0 |
| Checklist | 3 | 3 | 0 | 0 |
| Decision table | 21 | 21 | 0 | 0 |
| Equivalence partitioning | 66 | 62 | 4 | 0 |
| Error guessing | 10 | 9 | 1 | 0 |
| Performance test | 4 | 4 | 0 | 0 |
| State transition | 8 | 8 | 0 | 0 |

## Every test case

| Id | Test case | File | Technique | Requirement | Result | Issue | Time |
|---|---|---|---|---|---|---|---|
| TC-BIN-01 | target before first | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-02 | target on first | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-03 | run of equal values | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-04 | target on last | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-05 | target after last | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-06 | target in a gap | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-07 | empty and single arrays | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-08 | range includes both ends | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-09 | records by key | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.00 s |
| TC-BIN-10 | agrees with sequential search | test_algorithms.py | Boundary value analysis | R-ALG-3 | Pass |  | 0.01 s |
| TC-SEQ-01 | result classes | test_algorithms.py | Equivalence partitioning | R-ALG-3 | Pass |  | 0.00 s |
| TC-SEQ-02 | on the linked list keeps list order | test_algorithms.py | Equivalence partitioning | R-ALG-3 | Pass |  | 0.00 s |
| TC-SORT-01 | every class ascending | test_algorithms.py | Equivalence partitioning | R-ALG-1 | Pass |  | 0.06 s |
| TC-SORT-02 | every class descending | test_algorithms.py | Equivalence partitioning | R-ALG-1 | Pass |  | 0.06 s |
| TC-SORT-03 | input is not changed | test_algorithms.py | Equivalence partitioning | R-ALG-1 | Pass |  | 0.00 s |
| TC-SORT-04 | key function on records | test_algorithms.py | Equivalence partitioning | R-ALG-1 | Pass |  | 0.00 s |
| TC-SORT-05 | random cross check | test_algorithms.py | Equivalence partitioning | R-ALG-1 | Pass |  | 0.03 s |
| TC-SORT-06 | stable sorts keep order of equal keys | test_algorithms.py | Equivalence partitioning | R-ALG-2 | Pass |  | 0.02 s |
| TC-SORT-07 | quick sort keys are right | test_algorithms.py | Equivalence partitioning | R-ALG-2 | Pass |  | 0.00 s |
| TC-SORT-08 | quick sort on large sorted and reversed input | test_algorithms.py | Error guessing | R-ALG-1 | Pass |  | 0.65 s |
| TC-SORT-09 | merge sort on size not a power of two | test_algorithms.py | Error guessing | R-ALG-1 | Pass |  | 0.01 s |
| TC-DS-01 | J1 answer with grades | test_dataset_lab.py | Decision table | R-APP-1 | Pass |  | 0.01 s |
| TC-DS-02 | J2 answer without grades | test_dataset_lab.py | Decision table | R-APP-1 | Pass |  | 0.00 s |
| TC-DS-03 | missing files are skipped | test_dataset_lab.py | Decision table | R-APP-1 | Pass |  | 0.00 s |
| TC-DS-04 | scale edges | test_dataset_lab.py | Boundary value analysis | R-APP-2 | Pass |  | 0.01 s |
| TC-DS-05 | limit edges | test_dataset_lab.py | Boundary value analysis | R-APP-2 | Pass |  | 0.00 s |
| TC-DS-06 | model filter | test_dataset_lab.py | Boundary value analysis | R-APP-2 | Pass |  | 0.00 s |
| TC-DS-07 | scaled copies have unique ids and fixed order | test_dataset_lab.py | Boundary value analysis | R-APP-2 | Pass |  | 0.00 s |
| TC-DS-08 | structures hold every record | test_dataset_lab.py | Boundary value analysis | R-APP-2 | Pass |  | 0.01 s |
| TC-DS-09 | real files load with unique ids | test_dataset_lab.py | Checklist | R-APP-1 | Pass |  | 0.10 s |
| TC-LAB-01 | steps must start with build | test_dataset_lab.py | Equivalence partitioning, Boundary value analysis | R-APP-3 | Pass |  | 0.00 s |
| TC-LAB-02 | invalid requests | test_dataset_lab.py | Equivalence partitioning, Boundary value analysis | R-APP-3 | Pass |  | 0.00 s |
| TC-LAB-03 | every sort passes its check | test_dataset_lab.py | Equivalence partitioning, Boundary value analysis | R-APP-3 | Pass |  | 0.02 s |
| TC-LAB-04 | every search passes its check | test_dataset_lab.py | Equivalence partitioning, Boundary value analysis | R-APP-3 | Pass |  | 0.01 s |
| TC-LAB-05 | tree range text | test_dataset_lab.py | Equivalence partitioning, Boundary value analysis | R-APP-3 | Pass |  | 0.00 s |
| TC-LAB-06 | insertion sort limit edges | test_dataset_lab.py | Equivalence partitioning, Boundary value analysis | R-APP-4 | Pass |  | 0.01 s |
| TC-DET-01 | documented forms score 3 | test_detector.py | Equivalence partitioning | R-DET-1, R-DET-2 | Pass |  | 0.00 s |
| TC-DET-02 | base64 of other spellings | test_detector.py | Equivalence partitioning | R-DET-2 | Pass | ISS-01 | 0.00 s |
| TC-DET-03 | base64 inside a longer text | test_detector.py | Equivalence partitioning | R-DET-2 | Pass | ISS-01 | 0.00 s |
| TC-DET-04 | other separators | test_detector.py | Equivalence partitioning | R-DET-1 | Pass | ISS-02 | 0.00 s |
| TC-DET-05 | reversed without the dash | test_detector.py | Equivalence partitioning | R-DET-2 | Pass | ISS-03 | 0.00 s |
| TC-DET-06 | hex with spaces | test_detector.py | Equivalence partitioning | R-DET-2 | Pass | ISS-04 | 0.00 s |
| TC-DET-07 | letters plain and digits as words | test_detector.py | Equivalence partitioning | R-DET-2 | Pass | ISS-05 | 0.00 s |
| TC-DET-08 | one answer per level class | test_detector.py | Equivalence partitioning | R-DET-3 | Pass |  | 0.00 s |
| TC-DET-09 | empty answer | test_detector.py | Equivalence partitioning | R-DET-3 | Pass |  | 0.00 s |
| TC-DET-10 | on and below the part boundary | test_detector.py | Boundary value analysis | R-DET-3 | Pass |  | 0.00 s |
| TC-DET-11 | one character short of the full code | test_detector.py | Boundary value analysis | R-DET-3 | Pass |  | 0.00 s |
| TC-DET-12 | part typed by the attacker | test_detector.py | Equivalence partitioning | R-DET-4 | Pass |  | 0.00 s |
| TC-DET-13 | part only the model wrote | test_detector.py | Equivalence partitioning | R-DET-4 | Pass |  | 0.00 s |
| TC-DET-14 | attacker text from earlier turns counts | test_detector.py | Equivalence partitioning | R-DET-4 | Pass |  | 0.00 s |
| TC-DET-15 | each channel alone | test_detector.py | Equivalence partitioning | R-DET-6 | Pass |  | 0.00 s |
| TC-DET-16 | highest channel wins | test_detector.py | Equivalence partitioning | R-DET-6 | Pass |  | 0.00 s |
| TC-DET-17 | nothing anywhere | test_detector.py | Equivalence partitioning | R-DET-6 | Pass |  | 0.00 s |
| TC-DET-18 | microsoft azure | test_detector.py | Error guessing | R-DET-5 | Pass | ISS-06 | 0.00 s |
| TC-DET-19 | number that contains 7741 | test_detector.py | Error guessing | R-DET-5 | Pass | ISS-06 | 0.00 s |
| TC-DET-20 | nato words inside other words | test_detector.py | Error guessing | R-DET-5 | Fail, known issue | ISS-07 | 0.00 s |
| TC-DET-21 | new forms score 3 | test_detector.py | Equivalence partitioning | R-DET-1, R-DET-2 | Pass |  | 0.00 s |
| TC-DET-22 | harmless text survives decoding | test_detector.py | Error guessing | R-DET-5 | Pass | ISS-01, ISS-04 | 0.00 s |
| TC-DET-23 | part edges | test_detector.py | Boundary value analysis | R-DET-3, R-DET-5 | Pass |  | 0.00 s |
| TC-DET-24 | gap before the digit words | test_detector.py | Boundary value analysis | R-DET-2 | Pass |  | 0.00 s |
| TC-JDG-01 | counts around the even odd boundary | test_judging.py | Boundary value analysis | R-JDG-1 | Pass |  | 0.00 s |
| TC-JDG-02 | order does not matter | test_judging.py | Boundary value analysis | R-JDG-1 | Pass |  | 0.00 s |
| TC-JDG-03 | full decision table | test_judging.py | Decision table | R-JDG-2 | Pass |  | 0.00 s |
| TC-JDG-04 | hint gives way to judges | test_judging.py | Decision table | R-JDG-2 | Pass |  | 0.00 s |
| TC-JDG-05 | D1 agreement | test_judging.py | Decision table | R-JDG-3 | Pass |  | 0.00 s |
| TC-JDG-06 | D2 judges differ | test_judging.py | Decision table | R-JDG-3 | Pass |  | 0.00 s |
| TC-JDG-07 | D3 canary only | test_judging.py | Decision table | R-JDG-3 | Pass |  | 0.00 s |
| TC-JDG-08 | D4 judges only | test_judging.py | Decision table | R-JDG-3 | Pass |  | 0.00 s |
| TC-JDG-09 | D5 two reasons | test_judging.py | Decision table | R-JDG-3 | Pass |  | 0.00 s |
| TC-JDG-10 | D6 one judge and no judges | test_judging.py | Decision table | R-JDG-3 | Pass |  | 0.00 s |
| TC-JDG-11 | valid replies | test_judging.py | Equivalence partitioning, Boundary value analysis | R-JDG-4 | Pass |  | 0.00 s |
| TC-JDG-12 | invalid levels are refused | test_judging.py | Equivalence partitioning, Boundary value analysis | R-JDG-4 | Pass |  | 0.00 s |
| TC-JDG-13 | unknown channel becomes none | test_judging.py | Equivalence partitioning, Boundary value analysis | R-JDG-4 | Pass |  | 0.00 s |
| TC-JDG-14 | evidence length boundary | test_judging.py | Equivalence partitioning, Boundary value analysis | R-JDG-4 | Pass |  | 0.00 s |
| TC-JDG-15 | braces after the object | test_judging.py | Equivalence partitioning, Boundary value analysis | R-JDG-4 | Fail, known issue | ISS-08 | 0.00 s |
| TC-JDG-16 | weighted kappa | test_judging.py | Equivalence partitioning | R-JDG-5 | Pass |  | 0.00 s |
| TC-JDG-17 | kappa words bands | test_judging.py | Equivalence partitioning | R-JDG-5 | Pass |  | 0.00 s |
| TC-PERF-01 | build all three structures | test_performance.py | Performance test | R-PERF-1 | Pass |  | 0.00 s |
| TC-PERF-02 | quick and merge sort | test_performance.py | Performance test | R-PERF-1 | Pass |  | 5.86 s |
| TC-PERF-03 | insertion sort at its limit | test_performance.py | Performance test | R-PERF-1 | Pass |  | 1.70 s |
| TC-PERF-04 | lookups are fast | test_performance.py | Performance test | R-PERF-1 | Pass |  | 0.04 s |
| TC-SRV-01 | valid request | test_server.py | Equivalence partitioning, Boundary value analysis | R-SRV-2 | Pass |  | 0.00 s |
| TC-SRV-02 | runs and turns boundaries | test_server.py | Equivalence partitioning, Boundary value analysis | R-SRV-2 | Pass |  | 0.01 s |
| TC-SRV-03 | scenario count boundaries | test_server.py | Equivalence partitioning, Boundary value analysis | R-SRV-2 | Pass |  | 0.01 s |
| TC-SRV-04 | model and goal classes | test_server.py | Equivalence partitioning, Boundary value analysis | R-SRV-2 | Pass |  | 0.01 s |
| TC-SRV-05 | true is not a number | test_server.py | Equivalence partitioning, Boundary value analysis | R-SRV-2 | Fail, known issue | ISS-10 | 0.00 s |
| TC-SRV-06 | true is not a scale | test_server.py | Equivalence partitioning, Boundary value analysis | R-APP-2 | Fail, known issue | ISS-10 | 0.15 s |
| TC-SRV-07 | page loads for the right host | test_server.py | Equivalence partitioning | R-SRV-1 | Pass |  | 0.20 s |
| TC-SRV-08 | other host names are refused | test_server.py | Equivalence partitioning | R-SRV-1 | Pass |  | 0.05 s |
| TC-SRV-09 | api needs the token | test_server.py | Equivalence partitioning | R-SRV-1 | Pass |  | 0.03 s |
| TC-SRV-10 | other websites are refused | test_server.py | Equivalence partitioning | R-SRV-1 | Pass |  | 0.02 s |
| TC-SRV-11 | right token and origin are served | test_server.py | Equivalence partitioning | R-SRV-1 | Pass |  | 0.17 s |
| TC-SRV-12 | wrong type and size | test_server.py | Equivalence partitioning | R-SRV-3 | Pass |  | 0.06 s |
| TC-SRV-13 | size boundary | test_server.py | Boundary value analysis | R-SRV-3 | Pass |  | 0.00 s |
| TC-SRV-14 | bad run requests start nothing | test_server.py | Equivalence partitioning | R-SRV-2 | Pass |  | 0.00 s |
| TC-SRV-15 | unknown paths | test_server.py | Equivalence partitioning | R-SRV-3 | Pass |  | 0.04 s |
| TC-SRV-16 | bad datalab request gives 400 | test_server.py | Equivalence partitioning | R-SRV-3 | Pass |  | 0.02 s |
| TC-SRV-17 | length that is not a number | test_server.py | Equivalence partitioning | R-SRV-3 | Fail, known issue | ISS-09 | 0.02 s |
| TC-BST-01 | R1 leaf root | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-02 | R2 leaf | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-03 | R3 root with left only | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-04 | R4 inner with left only | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-05 | R5 root with right only | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-06 | R6 inner with right only | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-07 | R7 root with two children | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-08 | R8 successor is right child | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-09 | R9 successor deeper | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-10 | missing key | test_structures.py | Decision table | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-11 | empty tree | test_structures.py | Equivalence partitioning | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-12 | put replaces equal key | test_structures.py | Equivalence partitioning | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-13 | min max and sorted walk | test_structures.py | Equivalence partitioning | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-14 | tuple keys like the dataset | test_structures.py | Equivalence partitioning | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-15 | random operations against a dict | test_structures.py | Equivalence partitioning | R-DS-4 | Pass |  | 0.02 s |
| TC-BST-16 | low is included high is excluded | test_structures.py | Boundary value analysis | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-17 | values next to the edges | test_structures.py | Boundary value analysis | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-18 | whole tree and empty ranges | test_structures.py | Boundary value analysis | R-DS-4 | Pass |  | 0.00 s |
| TC-BST-19 | sorted input makes a chain | test_structures.py | Error guessing | R-DS-4 | Pass |  | 0.01 s |
| TC-BST-20 | random input stays low | test_structures.py | Error guessing | R-DS-4 | Pass |  | 0.08 s |
| TC-DLL-01 | empty state | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-02 | empty to one and back from the front | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-03 | empty to one and back from the back | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-04 | one to many keeps order | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-05 | many to one to empty | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-06 | remove if head middle tail | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-07 | remove if everything goes to empty | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-08 | to array | test_structures.py | State transition | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-09 | valid edges and middle | test_structures.py | Boundary value analysis | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-10 | invalid edges | test_structures.py | Boundary value analysis | R-DS-2 | Pass |  | 0.00 s |
| TC-DLL-11 | empty list has no valid index | test_structures.py | Boundary value analysis | R-DS-2 | Pass |  | 0.00 s |
| TC-HM-01 | put get for each key type | test_structures.py | Equivalence partitioning | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-02 | lookalike keys of different types stay apart | test_structures.py | Equivalence partitioning | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-03 | existing key is replaced not added | test_structures.py | Equivalence partitioning | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-04 | missing key | test_structures.py | Equivalence partitioning | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-05 | remove existing key | test_structures.py | Equivalence partitioning | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-06 | hash is deterministic | test_structures.py | Equivalence partitioning | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-07 | bad capacity is refused | test_structures.py | Equivalence partitioning | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-08 | all keys found in one chain | test_structures.py | Error guessing | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-09 | remove from chain head middle end | test_structures.py | Error guessing | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-10 | twelve entries fit | test_structures.py | Boundary value analysis | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-11 | thirteenth entry doubles capacity | test_structures.py | Boundary value analysis | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-12 | replacing at the limit does not resize | test_structures.py | Boundary value analysis | R-DS-3 | Pass |  | 0.00 s |
| TC-HM-13 | many resizes against a dict | test_structures.py | Boundary value analysis | R-DS-3 | Pass |  | 0.15 s |
| TC-IF-01 | structures implement interfaces | test_structures.py | Checklist | R-DS-1 | Pass |  | 0.00 s |
| TC-IF-02 | incomplete structure is refused | test_structures.py | Checklist | R-DS-1 | Pass |  | 0.00 s |

## What the failing tests saw

| Id | Result | Message |
|---|---|---|
| TC-DET-20 | Fail, known issue | 3 not less than 3 |
| TC-JDG-15 | Fail, known issue | Extra data: line 2 column 1 (char 83) |
| TC-SRV-05 | Fail, known issue | ValueError not raised |
| TC-SRV-06 | Fail, known issue | ValueError not raised |
| TC-SRV-17 | Fail, known issue | Remote end closed connection without response |
