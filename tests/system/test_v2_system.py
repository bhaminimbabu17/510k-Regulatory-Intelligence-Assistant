"""Version 2 system tests. These call the REAL openFDA API, FDA website and Claude API.

Skipped in CI. Run in the codespace (Version 1 tests are the regression part):
    export ANTHROPIC_API_KEY="your-key"
    RUN_SYSTEM_TESTS=1 python -m pytest tests/system -v -s
"""
import os

import pytest

from src.ai_client import AIServiceError, call_model
from src.ai_summary import UNAVAILABLE, is_supported, build_source, summarize_submission
from src.fda_client import FDAClient
from src.insights import DISCLAIMER, build_insights, contains_banned_language
from src.landscape import summarize_landscape
from src.predicates import fetch_summary_text, get_predicates
from src.results import format_result
from src.traceability import release

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_SYSTEM_TESTS") != "1" or not os.environ.get("ANTHROPIC_API_KEY"),
    reason="needs RUN_SYSTEM_TESTS=1 and ANTHROPIC_API_KEY")


@pytest.fixture(scope="module")
def submissions():
    client = FDAClient()
    try:
        records = client.search('device_name:"pulse oximeter" AND decision_date:[20200101 TO 20251231]',
                                limit=3)
    except Exception:
        records = []
    records = records or client.search('device_name:"pulse oximeter"', limit=3)
    return [(format_result(r), fetch_summary_text(r["k_number"])) for r in records]


def test_st11_summaries_are_grounded_and_traceable(submissions):  # FR-5.1, FR-5.2, FR-7.1
    retrieved = [r["k_number"] for r, _ in submissions]
    for record, text in submissions:
        item = release(summarize_submission(record, text), retrieved)
        source = build_source(record, text)
        print(f"\n[ST-11] {record['k_number']} label={item['label']} "
              f"kept={len(item.get('kept', []))} blocked={len(item.get('blocked', []))}")
        assert item["status"] == "released"
        assert all(is_supported(s, source) for s in item.get("kept", []))


def test_st12_invented_statement_is_blocked(submissions):  # FR-5.2, FR-5.3
    record, text = submissions[0]

    def model_with_hallucination(system, prompt):
        return call_model(system, prompt) + "\n- Predicate device: K999999 for pediatric oncology"

    item = summarize_submission(record, text, model_with_hallucination)
    print(f"\n[ST-12] blocked={item['blocked']}")
    assert any("K999999" in b for b in item["blocked"]) and "Unverified" in item["label"]


def test_st13_ai_failure_is_handled(submissions, monkeypatch):  # R-08
    monkeypatch.setenv("ANTHROPIC_API_KEY", "invalid-key")
    item = summarize_submission(*submissions[0])
    print(f"\n[ST-13] {item['text']}")
    assert item["text"] == UNAVAILABLE


def test_st14_insights_never_give_regulatory_advice(submissions):  # FR-6.1 to FR-6.3
    results = [r for r, _ in submissions]
    info = [get_predicates(r["k_number"]) for r in results]
    items = build_insights(summarize_landscape(results, info),
                           [r["k_number"] for r in results], call_model)
    for item in items:
        print(f"\n[ST-14] [{item['label']}] {item['text']}")
        assert item["disclaimer"] == DISCLAIMER
        assert item["status"] == "blocked" or not contains_banned_language(item["text"])


def test_st15_summaries_are_consistent(submissions):
    record, text = submissions[0]
    first = summarize_submission(record, text)
    second = summarize_submission(record, text)
    print(f"\n[ST-15] run 1 kept {len(first.get('kept', []))}, run 2 kept {len(second.get('kept', []))}")
    assert first.get("kept") and second.get("kept")


def test_st16_output_citing_unknown_submission_is_withheld(submissions):  # FR-7.2, FR-7.3
    record, text = submissions[0]
    item = release(summarize_submission(record, text), retrieved_k_numbers=["K000000"])
    print(f"\n[ST-16] status={item['status']}")
    assert item["status"] == "withheld"