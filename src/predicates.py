"""Predicate Extractor: finds predicate 510(k) numbers in summary PDFs.

Requirements: FR-4.1 (risk R-04). Predicates are not in the openFDA API,
so they are read from the 510(k) summary PDF on the FDA website.
"""
import io
import re

import requests
from pypdf import PdfReader

PDF_URL = "https://www.accessdata.fda.gov/cdrh_docs/{folder}/{k}.pdf"
K_NUMBER = re.compile(r"\bK\s?(\d{6})\b", re.IGNORECASE)
TIMEOUT_SECONDS = 15
HEADERS = {"User-Agent": "510k-Regulatory-Intelligence-Assistant (student project)"}

EXTRACTED = "Extracted"
NONE_FOUND = "None found in summary"
NOT_EXTRACTED = "Not extracted"  # FR-4.3


def summary_pdf_url(k_number):
    """FDA stores summaries in pdf<year>/ folders from 2002 on, and in pdf/ before that."""
    k = k_number.strip().upper()
    year = int(k[1:3]) if k[1:3].isdigit() else -1
    folder = f"pdf{year}" if 2 <= year <= 50 else "pdf"
    return PDF_URL.format(folder=folder, k=k)


def extract_predicates(text, own_k_number):
    """Return predicate K-numbers mentioned in the text, excluding the submission itself."""
    own = own_k_number.strip().upper()
    found = []
    for digits in K_NUMBER.findall(text or ""):
        k = f"K{digits}"
        if k != own and k not in found:
            found.append(k)
    return found


def fetch_summary_text(k_number, session=None):
    """Download and read the summary PDF. Returns None if it can't be read."""
    session = session or requests.Session()
    try:
        response = session.get(summary_pdf_url(k_number), headers=HEADERS,
                               timeout=TIMEOUT_SECONDS)
    except requests.RequestException:
        return None
    if response.status_code != 200 or not response.content.startswith(b"%PDF"):
        return None
    try:
        reader = PdfReader(io.BytesIO(response.content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:  # damaged or unreadable PDF
        return None
    return text if text.strip() else None  # scanned images have no text


def get_predicates(k_number, session=None):
    """Predicate info for one submission, always with a status and the PDF link."""
    text = fetch_summary_text(k_number, session)
    info = {"k_number": k_number, "pdf_url": summary_pdf_url(k_number), "predicates": []}
    if text is None:
        info["status"] = NOT_EXTRACTED
    else:
        info["predicates"] = extract_predicates(text, k_number)
        info["status"] = EXTRACTED if info["predicates"] else NONE_FOUND
    return info