from src.predicates import extract_predicates, summary_pdf_url
from src.results import NOT_AVAILABLE

SUMMARY = """510(k) Summary for K213456.
Predicate device: Acme Infusion System (K190001).
Reference device: k 182222. The subject device is compared to K190001 below."""


def test_extracts_predicates_and_skips_own_number():  # FR-4.1
    r = extract_predicates("K213456", SUMMARY)
    assert r.extracted
    assert r.predicates == ["K190001", "K182222"]


def test_no_text_means_extraction_failed():  # FR-4.2
    r = extract_predicates("K213456", None)
    assert not r.extracted
    assert r.predicates == []


def test_text_without_predicates_counts_as_failed():  # FR-4.2
    assert not extract_predicates("K213456", "A summary with no numbers.").extracted


def test_summary_pdf_link():  # FR-4.3
    assert summary_pdf_url("K213456") == "https://www.accessdata.fda.gov/cdrh_docs/pdf21/K213456.pdf"
    assert summary_pdf_url("K981234").endswith("/pdf/K981234.pdf")
    assert summary_pdf_url(NOT_AVAILABLE) == NOT_AVAILABLE
