# Version 1 system test (baseline v1.0.0)

- **Tester:**
- **Date:**
- **Commit / tag:**
- **CI run link:**

| # | Requirement | Test | Expected | Result (Pass/Fail) |
|---|---|---|---|---|
| 1 | FR-1.1 | `python -m src.app "infusion pump"` | Results include synonym matches (e.g. "infusion system") | |
| 2 | FR-1.1 | `python -m src.app FRN` | Results for product code FRN | |
| 3 | FR-1.2, FR-1.3 | `python -m src.app "rare widget device"` | Suggestions shown, never an empty page | |
| 4 | FR-2.1 | Any search | Results within 10 seconds | |
| 5 | FR-2.2 | Same search twice in one run (unit test `test_repeated_search_uses_cache`) | One API request | |
| 6 | FR-2.3 | Disconnect the network, run a search | "FDA data unavailable" error | |
| 7 | FR-3.1 | Any search | 510(k) number, name, applicant, date, product code, FDA link | |
| 8 | FR-3.2, FR-3.3 | Unit tests in `tests/test_results.py` | Missing fields show "Not available" | |
| 9 | FR-4.1 | `--landscape --summaries-dir` with one summary file | Predicates listed for that submission | |
| 10 | FR-4.2, FR-4.3 | `--landscape` without summary files | "INCOMPLETE", "Not extracted" and summary PDF links | |
| 11 | All | CI on `main` | All unit tests pass | |

**Outcome:** Pass / Fail. Version 1 is complete only when every row passes.
