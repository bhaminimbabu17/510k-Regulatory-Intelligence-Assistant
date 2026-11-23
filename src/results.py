"""Results Module: formats and filters 510(k) submissions.

Requirements: FR-3.1, FR-3.2, FR-3.3 (risk R-03).
"""
NOT_AVAILABLE = "Not available"  # FR-3.3
FDA_RECORD_URL = "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={k}"

# FR-3.1: the fields shown for every submission, in display order
FIELDS = [
    ("k_number", "510(k) number"),
    ("device_name", "Device name"),
    ("applicant", "Applicant"),
    ("decision_date", "Decision date"),
    ("product_code", "Product code"),
]


def _value(record, key):
    value = record.get(key)
    if value is None or str(value).strip() == "":
        return NOT_AVAILABLE  # FR-3.2 / FR-3.3: never show a blank
    return str(value).strip()


def format_result(record):
    """Return a display-ready submission with every field filled in."""
    result = {key: _value(record, key) for key, _ in FIELDS}
    k = result["k_number"]
    result["fda_link"] = FDA_RECORD_URL.format(k=k) if k != NOT_AVAILABLE else NOT_AVAILABLE
    result["missing_fields"] = [label for key, label in FIELDS if result[key] == NOT_AVAILABLE]
    return result


def filter_results(results, product_code=None, year_from=None, year_to=None):
    """Filter formatted results by product code and decision year."""
    kept = []
    for r in results:
        if product_code and r["product_code"].upper() != product_code.upper():
            continue
        year = r["decision_date"][:4]
        if (year_from or year_to) and not year.isdigit():
            continue
        if year_from and int(year) < year_from:
            continue
        if year_to and int(year) > year_to:
            continue
        kept.append(r)
    return kept


def format_table(results):
    """Plain-text table for the command line."""
    lines = []
    for r in results:
        lines.append(f"{r['k_number']}  {r['device_name']}")
        lines.append(f"    Applicant: {r['applicant']} | Decision: {r['decision_date']} "
                     f"| Product code: {r['product_code']}")
        lines.append(f"    FDA record: {r['fda_link']}")
    return "\n".join(lines)