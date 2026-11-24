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

def test_landscape_flag_shows_landscape_and_missing_predicates(capsys, tmp_path):  # FR-4.3
    (tmp_path / "K1.txt").write_text("ignored: not a valid K number", encoding="utf-8")
    (tmp_path / "K210001.txt").write_text("Predicate: K190001", encoding="utf-8")
    records = [record("K210001"), record("K220002"), record("K230003")]
    main(["infusion pump", "--landscape", "--summaries-dir", str(tmp_path)],
         client=StubClient(records))
    out = capsys.readouterr().out
    assert "Regulatory landscape (3 submission(s))" in out
    assert "K190001 (1)" in out
    assert "K220002: Not extracted" in out
