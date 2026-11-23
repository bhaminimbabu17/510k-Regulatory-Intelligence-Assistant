import pytest

from src.search import build_query, search_devices


class StubClient:
    def __init__(self, records):
        self.records = records
        self.queries = []

    def search(self, query, limit=20):
        self.queries.append(query)
        return self.records


def test_query_includes_synonyms():  # FR-1.1
    q = build_query("infusion pump")
    assert 'device_name:"infusion pump"' in q
    assert 'device_name:"infusion system"' in q
    assert " OR " in q


def test_three_letter_query_also_searches_product_code():  # FR-1.1
    assert "product_code:FRN" in build_query("frn")


def test_quotes_in_user_input_are_removed():
    assert build_query('pump"') == 'device_name:"pump"'


def test_enough_results_gives_no_suggestions():
    client = StubClient([{"k_number": f"K{i}"} for i in range(3)])
    assert search_devices("infusion pump", client).suggestions == []


def test_empty_result_always_has_suggestions():  # FR-1.2
    result = search_devices("rare widget device", StubClient([]))
    assert result.records == []
    assert result.suggestions


def test_few_results_suggest_broader_terms_and_product_code():  # FR-1.3
    result = search_devices("portable infusion pump", StubClient([{"product_code": "FRN"}]))
    text = " ".join(result.suggestions)
    assert '"portable"' in text and '"infusion"' in text
    assert "FRN" in text


def test_blank_query_is_rejected():
    with pytest.raises(ValueError):
        search_devices("   ", StubClient([]))