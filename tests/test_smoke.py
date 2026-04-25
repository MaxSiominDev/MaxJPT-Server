"""
Smoke tests against a live running server.

Run with:
    SMOKE_URL=http://your-vps API_KEY=your-key pytest -m smoke

Not executed in normal test runs.
"""

import os

import httpx
import pytest

BASE_URL = os.environ.get("SMOKE_URL", "http://localhost").rstrip("/")
API_KEY = os.environ.get("API_KEY", "")
AUTH = {"X-API-Key": API_KEY}

pytestmark = pytest.mark.smoke


def test_smoke_health() -> None:
    r = httpx.get(f"{BASE_URL}/health", headers=AUTH, timeout=10)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_smoke_chat() -> None:
    r = httpx.post(
        f"{BASE_URL}/chat",
        json={"user_prompt": "Reply with exactly one word: ready"},
        headers=AUTH,
        timeout=3600,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert body["status"] == "ok"
    assert isinstance(body["model_response"], str)
    assert len(body["model_response"]) > 0


def test_smoke_requests_page() -> None:
    r = httpx.get(f"{BASE_URL}/requests", headers=AUTH, timeout=10)
    assert r.status_code == 200
    assert "<table" in r.text


def test_smoke_unauthorized() -> None:
    r = httpx.post(f"{BASE_URL}/chat", json={"user_prompt": "hi"}, timeout=10)
    assert r.status_code == 401
    assert r.json() == {"status": "error", "message": "Unauthorized"}
