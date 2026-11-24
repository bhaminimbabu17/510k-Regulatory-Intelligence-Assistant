from src.results import NOT_AVAILABLE, filter_results, format_result, format_table
from tests.fakes import record


def test_all_fields_and_fda_link_present():  # FR-3.1
    r = format_result(record("K213456"))
    assert r["k_number"] == "K213456"
    assert r["fda_link"].endswith("ID=K213456")
    assert r["missing_fields"] == []


def test_missing_and_blank_fields_are_labelled():  # FR-3.2, FR-3.3
    r = format_result({"k_number": "K1", "applicant": "  "})
    assert r["applicant"] == NOT_AVAILABLE
    assert r["decision_date"] == NOT_AVAILABLE
    assert "Applicant" in r["missing_fields"]


def test_no_blank_values_ever_displayed():  # FR-3.2
    r = format_result({})
    assert all(str(v).strip() for v in r.values())


def test_filter_by_product_code_and_year():
    rs = [format_result(record("K1", product_code="FRN", decision_date="2019-01-01")),
          format_result(record("K2", product_code="MEB", decision_date="2022-01-01")),
          format_result(record("K3", product_code="FRN", decision_date="2023-06-01"))]
    assert [r["k_number"] for r in filter_results(rs, product_code="frn")] == ["K1", "K3"]
    assert [r["k_number"] for r in filter_results(rs, year_from=2020)] == ["K2", "K3"]
    assert [r["k_number"] for r in filter_results(rs, year_to=2020)] == ["K1"]


def test_table_shows_link():
    assert "FDA record:" in format_table([format_result(record())])
