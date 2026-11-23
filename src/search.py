"""Search Service: finds 510(k) submissions for a user's query.

Requirements: FR-1.1, FR-1.2, FR-1.3 (risk R-01).
"""
import re
from dataclasses import dataclass, field

from src.synonyms import synonyms_for

MIN_RESULTS = 3  # FR-1.3: fewer than this triggers suggestions
PRODUCT_CODE = re.compile(r"^[A-Za-z]{3}$")


@dataclass
class SearchResult:
    query: str
    records: list
    suggestions: list = field(default_factory=list)


def _quote(term):
    return '"' + term.replace('"', "") + '"'


def build_query(user_query):
    """Build an openFDA search string covering name, synonyms and product code (FR-1.1)."""
    term = user_query.strip()
    parts = [f"device_name:{_quote(term)}"]
    parts += [f"device_name:{_quote(s)}" for s in synonyms_for(term)]
    if PRODUCT_CODE.match(term):
        parts.append(f"product_code:{term.upper()}")
    return " OR ".join(parts)


def suggest_terms(user_query, records):
    """Suggest broader searches when results are few (FR-1.2, FR-1.3)."""
    words = [w for w in user_query.split() if len(w) > 2]
    suggestions = []
    if len(words) > 1:
        suggestions += [f'Try a broader term: "{w}"' for w in sorted(words, key=len, reverse=True)]
    suggestions += [f'Try a synonym: "{s}"' for s in synonyms_for(user_query)]
    codes = sorted({r.get("product_code") for r in records if r.get("product_code")})
    if codes:
        suggestions += [f"Try a product-code search: {c}" for c in codes]
    else:
        suggestions.append("Try a product-code search (a 3-letter FDA code, e.g. FRN)")
    return suggestions


def search_devices(user_query, client, limit=20):
    """Search openFDA and return records plus suggestions when results are few."""
    if not user_query.strip():
        raise ValueError("Enter a device name, description or product code.")
    records = client.search(build_query(user_query), limit=limit)
    suggestions = suggest_terms(user_query, records) if len(records) < MIN_RESULTS else []
    return SearchResult(query=user_query, records=records, suggestions=suggestions)