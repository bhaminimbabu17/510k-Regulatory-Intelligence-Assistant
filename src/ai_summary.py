"""Summary Service and Validator: source-grounded AI summaries.

Requirements: FR-5.1, FR-5.2, FR-5.3 (risk R-05); AI outage handling (R-08).
"""
import logging
import re

from src.ai_client import AIServiceError, call_model
from src.traceability import attach_sources

log = logging.getLogger(__name__)

MAX_SOURCE_CHARS = 12000
SUPPORT_THRESHOLD = 0.6  # share of a statement's key words that must appear in the source
UNVERIFIED = "Unverified"
UNAVAILABLE = "Summary unavailable (AI service error)"

SYSTEM_PROMPT = (
    "You summarize FDA 510(k) submissions for regulatory researchers. "
    "Use ONLY the source text provided. Do not add facts, numbers, device names or "
    "predicates that are not in the source. If something is not in the source, leave it out. "
    "Do not give regulatory advice or say which pathway a device qualifies for. "
    "Reply with 3 to 6 bullet points, each starting with '- ', covering intended use, "
    "device characteristics and predicate devices when the source mentions them."
)

STOPWORDS = {"this", "that", "with", "from", "which", "their", "there", "have", "been",
             "were", "will", "also", "into", "such", "used", "uses", "using", "device",
             "devices", "submission", "about", "these", "those", "than", "they", "when"}
NUMBERS = re.compile(r"\b(?:K\d{6}|\d[\d.,]*)\b", re.IGNORECASE)
WORDS = re.compile(r"[a-z][a-z\-]{3,}")


def build_source(record, summary_text=None):
    """The only text the model may use (FR-5.1)."""
    fields = "\n".join(f"{k}: {v}" for k, v in record.items()
                       if k in ("k_number", "device_name", "applicant", "decision_date",
                                "product_code"))
    text = fields
    if summary_text:
        text += "\n\n510(k) summary:\n" + summary_text[:MAX_SOURCE_CHARS]
    return text


def parse_bullets(reply):
    return [line.strip()[2:].strip() for line in reply.splitlines()
            if line.strip().startswith(("- ", "* ", "• "))]


def is_supported(statement, source):
    """FR-5.2: every number must appear in the source, and most key words too."""
    src = source.lower()
    for number in NUMBERS.findall(statement):
        if number.lower().rstrip(".,") not in src:
            return False
    words = [w for w in WORDS.findall(statement.lower()) if w not in STOPWORDS]
    if not words:
        return True
    found = sum(1 for w in words if w in src)
    return found / len(words) >= SUPPORT_THRESHOLD


def summarize_submission(record, summary_text=None, model=call_model):
    """Return a traceable summary item. Unsupported statements are blocked."""
    k = record.get("k_number", "")
    source = build_source(record, summary_text)
    try:
        reply = model(SYSTEM_PROMPT, f"Source:\n{source}\n\nSummarize this submission.")
    except AIServiceError as error:
        log.warning("AI summary failed for %s: %s", k, error)
        item = attach_sources(UNAVAILABLE, [k], label="Notice")
        item["status"] = "unavailable"
        return item

    bullets = parse_bullets(reply)
    kept = [b for b in bullets if is_supported(b, source)]
    blocked = [b for b in bullets if b not in kept]
    text = "\n".join(f"  - {b}" for b in kept) or "  (no statements could be verified)"
    label = "AI-generated"
    if blocked or not kept:  # FR-5.3
        label = f"AI-generated, {UNVERIFIED}"
        log.warning("Blocked %d unsupported statement(s) for %s: %s", len(blocked), k, blocked)
        text += f"\n  ({len(blocked)} statement(s) blocked: not supported by the source. " \
                "Check the FDA record linked below.)"
    item = attach_sources("Summary:\n" + text, [k], label=label)
    item["kept"], item["blocked"] = kept, blocked
    return item