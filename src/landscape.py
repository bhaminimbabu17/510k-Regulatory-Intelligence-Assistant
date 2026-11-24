"""Landscape Module: patterns across a set of 510(k) submissions.

Requirements: FR-4.2, FR-4.3 (risk R-04).
"""
from collections import Counter

from src.predicates import NOT_EXTRACTED
from src.results import NOT_AVAILABLE


def summarize_landscape(results, predicate_info=None):
    """Count recurring applicants, product codes, decision years and predicates."""
    def count(key):
        return Counter(r[key] for r in results if r[key] != NOT_AVAILABLE)

    summary = {
        "total": len(results),
        "applicants": count("applicant"),
        "product_codes": count("product_code"),
        "years": Counter(r["decision_date"][:4] for r in results
                         if r["decision_date"] != NOT_AVAILABLE),
        "predicates": Counter(),
        "predicates_complete": None,
        "not_extracted": [],
    }
    if predicate_info is not None:
        for info in predicate_info:
            summary["predicates"].update(info["predicates"])
            if info["status"] == NOT_EXTRACTED:
                summary["not_extracted"].append(info)
        summary["predicates_complete"] = not summary["not_extracted"]  # FR-4.2
    return summary


def format_landscape(summary, top=5):
    lines = [f"Regulatory landscape ({summary['total']} submissions)"]
    for title, key in [("Top applicants", "applicants"), ("Product codes", "product_codes"),
                       ("Decisions by year", "years")]:
        lines.append(f"\n{title}:")
        for name, n in summary[key].most_common(top):
            lines.append(f"  {name}: {n}")
    if summary["predicates_complete"] is not None:
        lines.append("\nMost-cited predicates:")
        for k, n in summary["predicates"].most_common(top):
            lines.append(f"  {k}: cited by {n}")
        if not summary["predicates"]:
            lines.append("  None found")
        if not summary["predicates_complete"]:  # FR-4.2 / FR-4.3
            missing = summary["not_extracted"]
            lines.append(f"\nPredicate list incomplete: {len(missing)} summary PDF(s) "
                         "could not be read. Predicates: Not extracted for:")
            for info in missing:
                lines.append(f"  {info['k_number']}: check {info['pdf_url']}")
    return "\n".join(lines)