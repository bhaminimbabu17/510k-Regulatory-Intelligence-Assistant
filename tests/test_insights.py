from src.ai_client import AIServiceError
from src.insights import (BLOCKED_MESSAGE, DISCLAIMER, build_insights,
                          contains_banned_language, format_insights)
from src.landscape import summarize_landscape
from src.predicates import EXTRACTED
from src.results import format_result
from tests.fakes import record

RESULTS = [format_result(record("K1", applicant="Co A")), format_result(record("K2", applicant="Co A"))]
INFO = [{"k_number": "K1", "status": EXTRACTED, "predicates": ["K9"], "pdf_url": "u"},
        {"k_number": "K2", "status": EXTRACTED, "predicates": ["K9"], "pdf_url": "u"}]
SUMMARY = summarize_landscape(RESULTS, INFO)


def test_describes_recurring_patterns():  # FR-6.1
    texts = [i["text"] for i in build_insights(SUMMARY, ["K1", "K2"])]
    assert "Most common applicant: Co A (2 of 2 submissions)" in texts
    assert "Most-cited predicate: K9 (cited by 2 submissions)" in texts


def test_every_insight_has_disclaimer_and_sources():  # FR-6.3, FR-7.1
    for item in build_insights(SUMMARY, ["K1", "K2"]):
        assert item["disclaimer"] == DISCLAIMER
        assert [s["k_number"] for s in item["sources"]] == ["K1", "K2"]


def test_ai_narrative_with_pathway_language_is_blocked():  # FR-6.2
    def model(system, prompt):
        return "This device qualifies for the 510(k) pathway."
    ai = build_insights(SUMMARY, ["K1"], model)[-1]
    assert ai["status"] == "blocked" and ai["text"] == BLOCKED_MESSAGE


def test_neutral_ai_narrative_is_kept():
    def model(system, prompt):
        return "Co A appears most often, and K9 is the most cited predicate."
    ai = build_insights(SUMMARY, ["K1"], model)[-1]
    assert ai["status"] == "released" and ai["label"] == "AI-generated insight"


def test_ai_failure_keeps_pattern_insights():
    def broken(system, prompt):
        raise AIServiceError("down")
    assert len(build_insights(SUMMARY, ["K1"], broken)) == 3


def test_banned_phrase_detection():
    assert contains_banned_language("It IS SUBSTANTIALLY EQUIVALENT to K1")
    assert not contains_banned_language("Several submissions cite K1 as a predicate")


def test_format_shows_disclaimer():
    assert DISCLAIMER in format_insights(build_insights(SUMMARY, ["K1"]))