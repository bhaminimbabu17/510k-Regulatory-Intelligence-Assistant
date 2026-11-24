"""Insights Module: patterns across submissions, never regulatory advice.

Requirements: FR-6.1, FR-6.2, FR-6.3 (risk R-06).
"""
import re

from src.ai_client import AIServiceError
from src.traceability import attach_sources

DISCLAIMER = ("For research only. This is not a regulatory pathway determination; "
              "a qualified person must review the FDA records.")  # FR-6.3
BLOCKED_MESSAGE = "Insight withheld: it contained regulatory-determination language."

# FR-6.2: wording that reads as a regulatory determination
BANNED_PHRASES = [
    "qualifies for", "should use the", "should pursue", "should file",
    "is substantially equivalent", "will be cleared", "will be approved",
    "recommend submitting", "you should submit", "is eligible for",
]

NARRATIVE_PROMPT = (
    "You describe patterns in FDA 510(k) data for researchers. Using only the patterns "
    "given, write 2 or 3 plain sentences describing them. Do not give regulatory advice, "
    "do not say which pathway a device qualifies for, and do not predict FDA decisions."
)


def contains_banned_language(text):
    lowered = text.lower()
    return any(re.search(r"\b" + re.escape(p) + r"\b", lowered) for p in BANNED_PHRASES)


def pattern_insights(summary):
    """FR-6.1: plain statements of recurring values."""
    total = summary["total"]
    lines = []
    for title, key in [("Most common applicant", "applicants"),
                       ("Most common product code", "product_codes")]:
        if summary[key]:
            name, n = summary[key].most_common(1)[0]
            lines.append(f"{title}: {name} ({n} of {total} submissions)")
    if summary["predicates"]:
        k, n = summary["predicates"].most_common(1)[0]
        lines.append(f"Most-cited predicate: {k} (cited by {n} submissions)")
    return lines


def _guarded(text, k_numbers):
    item = attach_sources(text, k_numbers, label="Insight")
    if contains_banned_language(text):  # FR-6.2
        item["text"], item["status"] = BLOCKED_MESSAGE, "blocked"
    item["disclaimer"] = DISCLAIMER  # FR-6.3
    return item


def build_insights(summary, k_numbers, model=None):
    """Insights from the landscape, plus an optional AI narrative, all guarded."""
    items = [_guarded(line, k_numbers) for line in pattern_insights(summary)]
    if model and items:
        patterns = "\n".join(i["text"] for i in items)
        try:
            narrative = model(NARRATIVE_PROMPT, f"Patterns:\n{patterns}")
            ai_item = _guarded(narrative.strip(), k_numbers)
            ai_item["label"] = "AI-generated insight"
            items.append(ai_item)
        except AIServiceError:
            pass  # pattern insights still shown (R-08)
    return items


def format_insights(items):
    lines = ["Insights:"]
    for item in items:
        lines.append(f"  [{item['label']}] {item['text']}")
    if items:
        lines.append(f"  Note: {DISCLAIMER}")
    return "\n".join(lines)