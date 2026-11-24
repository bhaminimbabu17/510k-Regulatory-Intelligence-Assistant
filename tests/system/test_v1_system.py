"""Version 1 system tests. These call the REAL openFDA API and FDA website.

They are skipped in CI. Run them in the codespace with:
    RUN_SYSTEM_TESTS=1 python -m pytest tests/system/test_v1_system.py -v -s
"""
import os

import pytest

from src import fda_client as fda_module
from src.app import main
from src.fda_client import FDAClient, FDADataUnavailable
from src.predicates import NOT_EXTRACTED, get_predicates
from src.results import NOT_AVAILABLE, filter_results, format_result
from src.search import build_query, search_devices

pytestmark = pytest.mark.skipif(os.environ.get("RUN_SYSTEM_TESTS") != "1",
                                reason="system tests call the live FDA API")

CATEGORIES = ["infusion pump", "glucose meter", "pulse oximeter"]


@pytest.fixture(scope="module")
def client():
    return FDAClient()


@pytest.mark.parametrize("term", CATEGORIES)
def test_st1_search_finds_results_across_device_categories(client, term):  # FR-1.1
    result = search_devices(term, client, limit=20)
    print(f"\n[ST-1] {term}: {len(result.records)} results")
    assert len(result.records) >= 3


def test_st2_synonyms_find_at_least_as_many_results(client):  # FR-1.1
    plain = client.search('device_name:"glucose meter"', limit=100)
    expanded = client.search(build_query("glucose meter"), limit=100)
    print(f"\n[ST-2] plain={len(plain)} with synonyms={len(expanded)}")
    assert len(expanded) >= len(plain)


def test_st3_product_code_search(client):  # FR-1.1
    result = search_devices("FRN", client, limit=20)
    print(f"\n[ST-3] FRN: {len(result.records)} results")
    assert any(r.get("product_code") == "FRN" for r in result.records)


def test_st4_no_match_gives_suggestions(client):  # FR-1.2, FR-1.3
    result = search_devices("zzqx nonexistent gadget", client)
    print(f"\n[ST-4] records={len(result.records)} suggestions={len(result.suggestions)}")
    assert result.records == [] and result.suggestions


def test_st5_no_blank_fields_in_live_data(client):  # FR-3.1, FR-3.2, FR-3.3
    results = [format_result(r) for r in search_devices("catheter", client, limit=100).records]
    missing = sum(len(r["missing_fields"]) for r in results)
    print(f"\n[ST-5] {len(results)} records checked, {missing} missing fields labelled")
    for r in results:
        assert all(str(v).strip() for v in r.values())
        assert r["fda_link"] != NOT_AVAILABLE


def test_st6_filter_by_product_code(client):
    results = [format_result(r) for r in search_devices("infusion pump", client, limit=100).records]
    filtered = filter_results(results, product_code="FRN")
    print(f"\n[ST-6] {len(results)} -> {len(filtered)} after FRN filter")
    assert filtered and all(r["product_code"] == "FRN" for r in filtered)


def test_st7_outage_is_reported(monkeypatch):  # FR-2.3
    monkeypatch.setattr(fda_module, "API_URL", "https://api.fda.gov.invalid/device/510k.json")
    with pytest.raises(FDADataUnavailable):
        FDAClient().search('device_name:"pump"')
    print("\n[ST-7] outage raised FDADataUnavailable")


def test_st8_predicate_extraction_always_reports_status(client):  # FR-4.1, FR-4.3
    try:  # recent submissions are more likely to have a readable summary PDF
        records = client.search('device_name:"pulse oximeter" AND decision_date:[20200101 TO 20251231]',
                                limit=5)
    except FDADataUnavailable:
        records = []
    records = records or client.search('device_name:"pulse oximeter"', limit=5)
    infos = [get_predicates(r["k_number"]) for r in records]
    for info in infos:
        print(f"\n[ST-8] {info['k_number']}: {info['status']} {info['predicates']}")
        assert info["status"]
        if info["status"] == NOT_EXTRACTED:
            assert info["pdf_url"].endswith(".pdf")


def test_st9_command_line_end_to_end(capsys):
    code = main(["infusion pump", "--landscape", "--limit", "10"])
    out = capsys.readouterr().out
    print(out[:400])
    assert code == 0 and "Regulatory landscape" in out