"""Landscape Module: regulatory landscape across the retrieved submissions.

Requirements: FR-4.2, FR-4.3 (risk R-04).
"""
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from src.predicates import extract_predicates
from src.results import NOT_AVAILABLE

NOT_EXTRACTED = "Not extracted"  # FR-4.3


@dataclass
class Landscape:
    total: int = 0
    applicants: Counter = field(default_factory=Counter)
    product_codes: Counter = field(default_factory=Counter)
    years: Counter = field(default_factory=Counter)
    predicates: Counter = field(default_factory=Counter)  # predicate -> citing submissions
    predicate_status: dict = field(default_factory=dict)  # k_number -> list or NOT_EXTRACTED
    failed: list = field(default_factory=list)  # PredicateResult for each failed extraction

    @property
    def predicates_complete(self):
        """FR-4.2: never complete if extraction failed for any submission."""
        return not self.failed


def load_summary_texts(directory, k_numbers):
    """Read <directory>/<K number>.txt for each submission; missing files are skipped."""
    texts = {}
    if not directory:
        return texts
    folder = Path(directory)
    for k in k_numbers:
        path = folder / f"{k}.txt"
        if path.is_file():
            texts[k] = path.read_text(encoding="utf-8", errors="replace")
    return texts


def build_landscape(results, summary_texts=None):
    """Summarize formatted results (from results.format_result)."""
    summary_texts = summary_texts or {}
    land = Landscape(total=len(results))
    for r in results:
        if r["applicant"] != NOT_AVAILABLE:
            land.applicants[r["applicant"]] += 1
        if r["product_code"] != NOT_AVAILABLE:
            land.product_codes[r["product_code"]] += 1
        year = r["decision_date"][:4]
        if year.isdigit():
            land.years[year] += 1

        k = r["k_number"]
        extraction = extract_predicates(k, summary_texts.get(k))
        if extraction.extracted:
            land.predicate_status[k] = extraction.predicates
            land.predicates.update(extraction.predicates)
        else:
            land.predicate_status[k] = NOT_EXTRACTED  # FR-4.3
            land.failed.append(extraction)
    return land


def _counts(counter, top=5):
    if not counter:
        return NOT_AVAILABLE
    return ", ".join(f"{name} ({count})" for name, count in counter.most_common(top))


def format_landscape(land):
    """Plain-text landscape view for the command line."""
    lines = [
        f"Regulatory landscape ({land.total} submission(s))",
        f"  Top applicants: {_counts(land.applicants)}",
        f"  Product codes: {_counts(land.product_codes)}",
        "  Decisions by year: "
        + (", ".join(f"{y} ({n})" for y, n in sorted(land.years.items())) or NOT_AVAILABLE),
    ]
    if land.predicates_complete:
        lines.append(f"  Predicates cited: {_counts(land.predicates)}")
    else:  # FR-4.2: label the list as incomplete
        lines.append(f"  Predicates cited (INCOMPLETE): {_counts(land.predicates)}")
        lines.append(f"  Predicates could not be extracted for {len(land.failed)} "
                     "submission(s); check the summary PDFs:")
        for f in land.failed:  # FR-4.3
            lines.append(f"    {f.k_number}: {NOT_EXTRACTED} - summary PDF: {f.summary_pdf}")
    return "\n".join(lines)
