from src.landscape import (NOT_EXTRACTED, build_landscape, format_landscape,
                           load_summary_texts)
from src.results import format_result
from tests.fakes import record


def results():
    return [
        format_result(record("K210001", applicant="Acme", decision_date="2021-02-01")),
        format_result(record("K220002", applicant="Acme", decision_date="2022-03-01")),
        format_result(record("K230003", applicant="Beta Med", product_code="MEB",
                             decision_date="2023-04-01")),
    ]


ALL_TEXTS = {
    "K210001": "Predicate: K190001",
    "K220002": "Predicate device K190001 and K200009",
    "K230003": "Predicate K200009",
}


def test_counts_applicants_codes_years_and_predicates():
    land = build_landscape(results(), ALL_TEXTS)
    assert land.applicants["Acme"] == 2
    assert land.product_codes["FRN"] == 2 and land.product_codes["MEB"] == 1
    assert land.years == {"2021": 1, "2022": 1, "2023": 1}
    assert land.predicates["K190001"] == 2
    assert land.predicates_complete


def test_missing_summary_marks_not_extracted():  # FR-4.2, FR-4.3
    texts = dict(ALL_TEXTS)
    del texts["K230003"]
    land = build_landscape(results(), texts)
    assert not land.predicates_complete
    assert land.predicate_status["K230003"] == NOT_EXTRACTED
    text = format_landscape(land)
    assert "INCOMPLETE" in text
    assert "K230003: Not extracted" in text
    assert "cdrh_docs/pdf23/K230003.pdf" in text


def test_complete_landscape_is_not_labelled_incomplete():
    assert "INCOMPLETE" not in format_landscape(build_landscape(results(), ALL_TEXTS))


def test_load_summary_texts(tmp_path):
    (tmp_path / "K210001.txt").write_text("Predicate K190001", encoding="utf-8")
    assert load_summary_texts(tmp_path, ["K210001", "K999999"]) == {"K210001": "Predicate K190001"}
    assert load_summary_texts(None, ["K210001"]) == {}
