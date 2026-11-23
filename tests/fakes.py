"""Fake HTTP objects so tests never call the real openFDA API."""
import requests


class FakeResponse:
    def __init__(self, status_code=200, payload=None, content=b""):
        self.status_code = status_code
        self._payload = payload or {}
        self.content = content

    def json(self):
        return self._payload


class FakeSession:
    """Returns queued responses and records every call."""

    def __init__(self, responses=None, error=None):
        self.responses = list(responses or [])
        self.error = error
        self.calls = []

    def get(self, url, params=None, timeout=None, headers=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        if self.error:
            raise self.error
        return self.responses.pop(0)


def record(k_number="K000001", **fields):
    base = {
        "k_number": k_number,
        "device_name": "Generic Infusion Pump",
        "applicant": "Example Medical Inc.",
        "decision_date": "2021-05-04",
        "product_code": "FRN",
    }
    base.update(fields)
    return base


def timeout_error():
    return requests.Timeout("timed out")