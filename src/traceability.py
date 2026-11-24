"""Traceability Module: links every AI output to its FDA sources.

Requirements: FR-7.1, FR-7.2, FR-7.3 (risk R-07).
"""
from src.results import FDA_RECORD_URL

AI_LABEL = "AI-generated"
WITHHELD_MESSAGE = "Source could not be verified"  # FR-7.3


def attach_sources(text, k_numbers, label=AI_LABEL):
    """Wrap AI text with its source 510(k) numbers and FDA links (FR-7.1)."""
    sources = [{"k_number": k, "fda_link": FDA_RECORD_URL.format(k=k)}
               for k in dict.fromkeys(k_numbers) if k]
    return {"text": text, "label": label, "sources": sources, "status": "released"}


def release(item, retrieved_k_numbers):
    """Only release AI output whose sources are all among the retrieved submissions."""
    retrieved = set(retrieved_k_numbers)
    sources = [s["k_number"] for s in item["sources"]]
    if not sources or not set(sources) <= retrieved:  # FR-7.2
        return {**item, "text": WITHHELD_MESSAGE, "status": "withheld"}  # FR-7.3
    return item


def format_ai_output(item):
    lines = [f"[{item['label']}] {item['text']}"]
    if item["sources"]:
        lines.append("  Sources: " + ", ".join(f"{s['k_number']} ({s['fda_link']})"
                                              for s in item["sources"]))
    return "\n".join(lines)