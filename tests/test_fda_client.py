import pytest

from src.fda_client import TIMEOUT_SECONDS, FDAClient, FDADataUnavailable
from tests.fakes import FakeResponse, FakeSession, record, timeout_error


def test_returns_records_and_uses_timeout():  # FR-2.1
    session = FakeSession([FakeResponse(200, {"results": [record()]})])
    records = FDAClient(session=session).search('device_name:"pump"')
    assert records[0]["k_number"] == "K000001"
    assert session.calls[0]["timeout"] == TIMEOUT_SECONDS


def test_repeated_search_uses_cache():  # FR-2.2
    session = FakeSession([FakeResponse(200, {"results": [record()]})])
    client = FDAClient(session=session)
    client.search("q")
    client.search("q")
    assert len(session.calls) == 1


def test_sends_api_key_when_configured():  # FR-2.2
    session = FakeSession([FakeResponse(200, {"results": []})])
    FDAClient(session=session, api_key="abc").search("q")
    assert session.calls[0]["params"]["api_key"] == "abc"


def test_no_matches_returns_empty_list():
    session = FakeSession([FakeResponse(404)])
    assert FDAClient(session=session).search("q") == []


def test_server_error_raises_unavailable():  # FR-2.3
    session = FakeSession([FakeResponse(500)])
    with pytest.raises(FDADataUnavailable):
        FDAClient(session=session).search("q")


def test_timeout_raises_unavailable():  # FR-2.3
    with pytest.raises(FDADataUnavailable):
        FDAClient(session=FakeSession(error=timeout_error())).search("q")