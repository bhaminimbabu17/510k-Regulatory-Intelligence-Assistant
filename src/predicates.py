"""Predicate Extractor: finds predicate 510(k) numbers in a submission's summary text.

Requirements: FR-4.1 (risk R-04).
Predicates are not in the openFDA API; they appear in the 510(k) summary document.
"""
import re
from dataclasses import dataclass, field

from src.results import NOT_AVAILABLE

K_NUMBER_IN_TEXT = re.compile(r"\b[Kk]\s?(\d{6})\b")
VALID_K_NUMBER = re.compile(r"^K\d{6}$")
SUMMARY_PDF_URL = "https://www.accessdata.fda.gov/cdrh_docs/{folder}/{k}.pdf"


@dataclass
class PredicateResult:
    k_number: str
    predicates: list = field(default_factory=list)
    extracted: bool = False  # False means extraction failed (FR-4.2)
    summary_pdf: str = NOT_AVAILABLE


def summary_pdf_url(k_number):
    """Link to the FDA 510(k) summary PDF (FR-4.3).

    FDA stores 2002-2079 summaries in pdf2 ... pdf79 folders and older ones in pdf/.
    """
    k = str(k_number).strip().upper()
    if not VALID_K_NUMBER.match(k):
        return NOT_AVAILABLE
    year = int(k[1:3])
    folder = f"pdf{year}" if 2 <= year <= 79 else "pdf"
    return SUMMARY_PDF_URL.format(folder=folder, k=k)


def extract_predicates(k_number, summary_text):
    """Return the predicate 510(k) numbers cited in the summary text (FR-4.1).

    Extraction counts as failed when there is no text or no predicate is found,
    because every 510(k) clearance is based on at least one predicate.
    """
    result = PredicateResult(k_number=k_number, summary_pdf=summary_pdf_url(k_number))
    if not summary_text or not summary_text.strip():
        return result

    own = str(k_number).strip().upper()
    found = []
    for digits in K_NUMBER_IN_TEXT.findall(summary_text):
        k = "K" + digits
        if k != own and k not in found:
            found.append(k)

    result.predicates = found
    result.extracted = bool(found)
    return result
