# Version 2 System Test Report

- **Date run:** 2026-11-23
- **Tester:** Bhamini
- **Commit tested:** (output of `git rev-parse --short HEAD`)
- **AI model:** claude-haiku-5-5 (or the value of AI_MODEL, if you set one)
- **Command:** `RUN_SYSTEM_TESTS=1 python -m pytest tests/system -v -s`
- **Environment:** Linux codespace, Python 3.14.2, pytest 9.2.0

## Version 1 regression

| Test | Result |
|---|---|
| ST-1 to ST-9 (Version 1 system tests) | 11 of 11 passed, with the same results as the v1.0.0 test (see V1_system_test.md) |

## Version 2 tests

| Test | Requirement | What is tested | Result | Evidence (numbers printed by the test) |
|---|---|---|---|---|
| ST-11 | FR-5.1, FR-5.2, FR-7.1 | Summaries of 3 real submissions: every shown statement is supported by the source and linked to it | Pass (see observation) | K211140: 3 statements kept, 0 blocked. K193350: 2 kept, 0 blocked. K202743: 0 kept, 0 blocked, labelled "Unverified". All 3 released with source links |
| ST-12 | FR-5.2, FR-5.3 | An invented statement is blocked and the summary is labelled Unverified | Pass | Inserted "Predicate device: K999999 for pediatric oncology" was blocked |
| ST-13 | R-08 | AI service failure shows "Summary unavailable" | Pass | Invalid key produced "Summary unavailable (AI service error)" |
| ST-14 | FR-6.1 to FR-6.3 | Insights carry the disclaimer and never contain pathway-determination language | Pass | 3 pattern insights and 1 AI narrative; none contained determination language; all carried the disclaimer |
| ST-15 | Consistency | Two runs on the same submission both produce verified statements | Pass | Run 1 kept 4 statements; run 2 kept 4 |
| ST-16 | FR-7.2, FR-7.3 | Output citing a submission outside the results is withheld | [confirm: Pass] | [confirm: status=withheld] |

**Unit tests:** 55 passed, 17 skipped (CI run #__)

**Summary:** [17] of 17 system test cases passed (11 regression + 6 Version 2).

**Observation (ST-11):** For K202743 the AI reply contained no statements in the expected bullet format, so nothing could be verified. The system handled it safely: it labelled the summary "Unverified" and showed the FDA link instead of unchecked text. This meets FR-5.3, but it means 1 of 3 summaries gave the user no content. Possible improvement for a future CR: accept more bullet formats, such as numbered lists, before validating.

**Defects found:** None that violated a requirement.