from src.ai_client import AIServiceError, call_model
from src.ai_summary import (UNAVAILABLE, build_source, is_supported, parse_bullets,
                            summarize_submission)
from tests.fakes import FakeResponse, record

SUMMARY = "The Example Pump is intended for intravenous infusion of fluids. Predicate: K190001."


def fake_model(reply):
    def model(system, prompt):
        assert "Use ONLY the source text" in system
        assert SUMMARY in prompt  # FR-5.1: the source is sent
        return reply
    return model


def test_prompt_contains_only_record_and_summary():  # FR-5.1
    src = build_source(record("K213456", extra="ignored"), SUMMARY)
    assert "K213456" in src and SUMMARY in src and "ignored" not in src


def test_supported_statements_are_kept():
    item = summarize_submission(record("K213456"), SUMMARY, fake_model(
        "- Intended for intravenous infusion of fluids\n- Predicate device: K190001"))
    assert item["blocked"] == [] and len(item["kept"]) == 2
    assert item["label"] == "AI-generated"
    assert item["sources"][0]["k_number"] == "K213456"


def test_invented_number_is_blocked_and_labelled_unverified():  # FR-5.2, FR-5.3
    item = summarize_submission(record("K213456"), SUMMARY, fake_model(
        "- Intended for intravenous infusion of fluids\n- Predicate device: K999999"))
    assert item["blocked"] == ["Predicate device: K999999"]
    assert "Unverified" in item["label"] and "1 statement(s) blocked" in item["text"]


def test_invented_words_are_blocked():  # FR-5.2
    assert not is_supported("Approved for pediatric oncology chemotherapy", SUMMARY)
    assert is_supported("Intended for intravenous infusion", SUMMARY)


def test_ai_failure_gives_unavailable_notice():  # R-08
    def broken(system, prompt):
        raise AIServiceError("down")
    item = summarize_submission(record("K1"), SUMMARY, broken)
    assert item["status"] == "unavailable" and item["text"] == UNAVAILABLE


def test_parse_bullets():
    assert parse_bullets("Intro\n- one\n* two\nnot a bullet") == ["one", "two"]


def test_call_model_without_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    try:
        call_model("s", "p")
        assert False
    except AIServiceError:
        pass


def test_call_model_reads_text_reply(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    class Session:
        def post(self, url, json=None, headers=None, timeout=None):
            assert headers["x-api-key"] == "test"
            return FakeResponse(200, {"content": [{"type": "text", "text": "- hi"}]})

    assert call_model("s", "p", session=Session()) == "- hi"


def test_call_model_http_error(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    class Session:
        def post(self, *a, **k):
            return FakeResponse(401)

    try:
        call_model("s", "p", session=Session())
        assert False
    except AIServiceError:
        pass