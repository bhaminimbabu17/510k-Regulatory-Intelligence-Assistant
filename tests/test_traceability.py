from src.traceability import WITHHELD_MESSAGE, attach_sources, format_ai_output, release


def test_sources_and_links_attached():  # FR-7.1
    item = attach_sources("summary", ["K1", "K1", "K2"])
    assert [s["k_number"] for s in item["sources"]] == ["K1", "K2"]
    assert item["sources"][0]["fda_link"].endswith("ID=K1")
    assert item["label"] == "AI-generated"


def test_output_with_known_sources_is_released():
    item = release(attach_sources("summary", ["K1"]), ["K1", "K2"])
    assert item["status"] == "released" and item["text"] == "summary"


def test_output_without_sources_is_withheld():  # FR-7.2, FR-7.3
    item = release(attach_sources("summary", []), ["K1"])
    assert item["status"] == "withheld" and item["text"] == WITHHELD_MESSAGE


def test_output_citing_unknown_submission_is_withheld():  # FR-7.2
    assert release(attach_sources("x", ["K1", "K9"]), ["K1"])["status"] == "withheld"


def test_formatted_output_shows_label_and_sources():
    text = format_ai_output(attach_sources("summary", ["K1"]))
    assert "[AI-generated]" in text and "K1" in text