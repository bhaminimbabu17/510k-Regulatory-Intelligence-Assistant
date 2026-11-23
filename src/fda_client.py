"""FDA Client: retrieves 510(k) records from the openFDA API.

Requirements: FR-2.1, FR-2.2, FR-2.3 (risk R-02).
"""
import os

import requests

API_URL = "https://api.fda.gov/device/510k.json"
TIMEOUT_SECONDS = 10  # FR-2.1


class FDADataUnavailable(Exception):
    """Raised when openFDA cannot be reached or returns an error (FR-2.3)."""


class FDAClient:
    def __init__(self, session=None, api_key=None):
        self.session = session or requests.Session()
        self.api_key = api_key or os.environ.get("OPENFDA_API_KEY")
        self._cache = {}  # FR-2.2: identical requests are answered from memory

    def search(self, query, limit=20):
        """Run an openFDA search. Returns a list of records (may be empty)."""
        params = {"search": query, "limit": limit}
        if self.api_key:
            params["api_key"] = self.api_key  # FR-2.2
        cache_key = (query, limit)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            response = self.session.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)
        except requests.RequestException as error:
            raise FDADataUnavailable(f"FDA data unavailable: {error}") from error

        if response.status_code == 404:
            records = []  # openFDA answers "no matches" with 404
        elif response.status_code != 200:
            raise FDADataUnavailable(
                f"FDA data unavailable: openFDA returned HTTP {response.status_code}"
            )
        else:
            records = response.json().get("results", [])

        self._cache[cache_key] = records
        return records