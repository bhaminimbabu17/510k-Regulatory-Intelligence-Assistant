"""AI Client: sends a prompt to the Claude Messages API.

Set your key in the codespace terminal before using AI features:
    export ANTHROPIC_API_KEY="your-key"
Optional: export AI_MODEL="claude-haiku-5-5"  (check current model names at
https://docs.claude.com/en/docs/about-claude/models)
"""
import os

import requests

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-haiku-5-5"
TIMEOUT_SECONDS = 60


class AIServiceError(Exception):
    """Raised when the AI service is unavailable or returns an error."""


def call_model(system, prompt, max_tokens=600, session=None):
    """Return the model's text reply, or raise AIServiceError."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise AIServiceError("ANTHROPIC_API_KEY is not set")
    session = session or requests.Session()
    body = {
        "model": os.environ.get("AI_MODEL", DEFAULT_MODEL),
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"x-api-key": api_key, "anthropic-version": API_VERSION,
               "content-type": "application/json"}
    try:
        response = session.post(API_URL, json=body, headers=headers, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as error:
        raise AIServiceError(f"AI service unreachable: {error}") from error
    if response.status_code != 200:
        raise AIServiceError(f"AI service returned HTTP {response.status_code}")
    parts = response.json().get("content", [])
    return "".join(p.get("text", "") for p in parts if p.get("type") == "text")