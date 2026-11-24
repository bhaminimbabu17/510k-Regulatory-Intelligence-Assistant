# Version 1 System Test Report

- **Date run:** 2026-11-23
- **Tester:** Bhamini
- **Commit tested:** (output of `git rev-parse --short HEAD`)
- **Command:** `RUN_SYSTEM_TESTS=1 python -m pytest tests/system/test_v1_system.py -v -s`

| Test | Requirement | What is tested | Result | Evidence (numbers printed by the test) |
|---|---|---|---|---|
| ST-1 | FR-1.1 | Search returns results for infusion pump, glucose meter, pulse oximeter | Pass (3 of 3) | 20 results for each category (the requested limit of 20) |
| ST-2 | FR-1.1 | Synonyms find at least as many results as the plain name | Pass | "glucose meter": 49 results plain, 100 with synonyms (limit 100) |
| ST-3 | FR-1.1 | Product-code search (FRN) | Pass | 20 results, including product code FRN |
| ST-4 | FR-1.2, FR-1.3 | A query with no matches gives suggestions | Pass | 0 records, 4 suggestions |
| ST-5 | FR-3.1 to FR-3.3 | No blank fields in 100 live records; missing fields labelled | Pass | 100 records checked; 1 missing field shown as "Not available"; no blanks |
| ST-6 | FR-3.1 | Filtering by product code | Pass | 100 results filtered to 62 with product code FRN only |
| ST-7 | FR-2.3 | FDA outage is reported clearly | Pass | Unreachable FDA address raised "FDA data unavailable" |
| ST-8 | FR-4.1, FR-4.3 | Predicate extraction reports a status for every submission | Pass | 5 of 5 summary PDFs read: K211140 → K081238, K060143; K193350 → K112843; K202743 → K191403; K230172 → K181503; K221979 → K173123 |
| ST-9 | All V1 | Command line works end to end | Pass | "infusion pump" search with --landscape returned 10 submissions and the landscape view |

**Unit tests:** 32 passed (CI run #__)

**Summary:** 11 of 11 system test cases passed (ST-1 runs once per category).

**Defects found:** One found before this test run: the results test file was named `tests_results.py`, so pytest did not run its tests. It was renamed to `test_results.py` in CR-005. No defects found during system testing.