from src.predicates import (EXTRACTED, NONE_FOUND, NOT_EXTRACTED, extract_predicates,
                            get_predicates, summary_pdf_url)
from tests.fakes import FakeResponse, FakeSession, make_pdf, timeout_error


def test_pdf_url_uses_year_folder():
    assert summary_pdf_url("K213456").endswith("/pdf21/K213456.pdf")
    assert summary_pdf_url("K051234").endswith("/pdf5/K051234.pdf")
    assert summary_pdf_url("K992551").endswith("/pdf/K992551.pdf")


def test_extracts_predicates_but_not_itself():  # FR-4.1
    text = "This device (K213456) is equivalent to K190001 and K 181234. See K190001."
    assert extract_predicates(text, "K213456") == ["K190001", "K181234"]


def test_reads_predicates_from_pdf():  # FR-4.1
    session = FakeSession([FakeResponse(200, content=make_pdf("Predicate device: K190001"))])
    info = get_predicates("K213456", session)
    assert info["status"] == EXTRACTED
    assert info["predicates"] == ["K190001"]


def test_pdf_without_k_numbers():
    session = FakeSession([FakeResponse(200, content=make_pdf("No numbers here"))])
    assert get_predicates("K213456", session)["status"] == NONE_FOUND


def test_missing_pdf_is_not_extracted_with_link():  # FR-4.3
    info = get_predicates("K213456", FakeSession([FakeResponse(404)]))
    assert info["status"] == NOT_EXTRACTED
    assert info["pdf_url"].endswith("K213456.pdf")


def test_non_pdf_and_timeout_are_not_extracted():  # FR-4.3
    html = FakeSession([FakeResponse(200, content=b"<html>error</html>")])
    assert get_predicates("K213456", html)["status"] == NOT_EXTRACTED
    assert get_predicates("K213456", FakeSession(error=timeout_error()))["status"] == NOT_EXTRACTED