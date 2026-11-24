from src.app import main
from src.fda_client import FDADataUnavailable
from tests.fakes import record


class StubClient:
    def __init__(self, records=None, error=None):
        self.records, self.error = records or [], error

    def search(self, query, limit=20):
        if self.error:
            raise self.error
        return self.records


def test_prints_results_and_disclaimer(capsys):
    code = main(["infusion pump"], client=StubClient([record("K1"), record("K2"), record("K3")]))
    out = capsys.readouterr().out
    assert code == 0
    assert "3 submission(s)" in out and "K2" in out
    assert "Research support only" in out


def test_shows_suggestions_when_few_results(capsys):
    main(["rare widget"], client=StubClient([]))
    assert "Suggestions:" in capsys.readouterr().out


def test_fda_outage_shows_clear_error(capsys):  # FR-2.3
    code = main(["pump"], client=StubClient(error=FDADataUnavailable("FDA data unavailable: down")))
    assert code == 1
    assert "FDA data unavailable" in capsys.readouterr().out


def test_landscape_flag(capsys):
    main(["pump", "--landscape"], client=StubClient([record("K1"), record("K2"), record("K3")]))
    assert "Regulatory landscape (3 submissions)" in capsys.readouterr().out

def test_summarize_flag(capsys):
    class PdfSession:
        def get(self, *a, **k):
            from tests.fakes import FakeResponse
            return FakeResponse(404)

def model(system, prompt):
    return "- Generic Infusion Pump"

    main(["pump", "--summarize", "1"],
    client=StubClient([record("K1"), record("K2"), record("K3")]),
    pdf_session=PdfSession(), model=model)
    out = capsys.readouterr().out
    assert "[AI-generated] Summary:" in out and "Sources: K1" in out

def test_insights_flag(capsys):
    def model(system, prompt):
        return "Example Medical Inc. appears in every submission."

    main(["pump", "--insights"], client=StubClient([record("K1"), record("K2"), record("K3")]),
        model=model)
    out = capsys.readouterr().out
    assert "Insights:" in out and "For research only" in out
    assert "[AI-generated insight]" in out