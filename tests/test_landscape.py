from src.landscape import format_landscape, summarize_landscape
from src.predicates import EXTRACTED, NOT_EXTRACTED
from src.results import format_result
from tests.fakes import record

RESULTS = [format_result(record("K1", applicant="Co A", product_code="FRN")),
           format_result(record("K2", applicant="Co A", product_code="MEB")),
           format_result(record("K3", applicant=None, decision_date=None))]


def test_counts_recurring_values_and_skips_missing():
    s = summarize_landscape(RESULTS)
    assert s["applicants"]["Co A"] == 2
    assert "Not available" not in s["applicants"]
    assert s["predicates_complete"] is None


def test_complete_predicates():
    info = [{"k_number": "K1", "status": EXTRACTED, "predicates": ["K9"], "pdf_url": "u1"},
            {"k_number": "K2", "status": EXTRACTED, "predicates": ["K9"], "pdf_url": "u2"}]
    s = summarize_landscape(RESULTS[:2], info)
    assert s["predicates"]["K9"] == 2 and s["predicates_complete"] is True
    assert "incomplete" not in format_landscape(s)


def test_failed_extraction_marks_list_incomplete():  # FR-4.2, FR-4.3
    info = [{"k_number": "K1", "status": EXTRACTED, "predicates": ["K9"], "pdf_url": "u1"},
            {"k_number": "K2", "status": NOT_EXTRACTED, "predicates": [], "pdf_url": "http://pdf/K2"}]
    s = summarize_landscape(RESULTS[:2], info)
    text = format_landscape(s)
    assert s["predicates_complete"] is False
    assert "Predicate list incomplete" in text and "http://pdf/K2" in text