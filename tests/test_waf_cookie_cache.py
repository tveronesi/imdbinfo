"""Tests for the WAF cookie in-memory + on-disk cache in services.py.

Covered behaviours
──────────────────
1. _load_waf_cookies — first call reads the disk file and populates the
   in-memory cache (_waf_cookies).
2. _load_waf_cookies — subsequent calls in the same process skip the file
   and return straight from memory.
3. _load_waf_cookies — returns None (without raising) when no cache file
   exists and leaves _waf_cookies = None.
4. _save_waf_cookies — updates both the in-memory variable and the disk file.
5. _delete_waf_cookie_file — sets in-memory to None and removes the file.
6. request_handler — sends the cached cookies on a 200 response and keeps
   them intact.
7. request_handler — on a non-200 response invalidates the old cookies,
   calls the WAF solver, saves fresh cookies, and retries.
8. request_handler — if the retry after WAF solve also fails the cookies
   are discarded (memory = None, file deleted).
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from imdbinfo import services


# ── helpers ──────────────────────────────────────────────────────────────────


def _reset_cookie_state(monkeypatch, cookie_file: Path):
    """Point the module at a temp file path and reset the in-memory cache."""
    monkeypatch.setattr(services, "_WAF_COOKIE_FILE", cookie_file)
    monkeypatch.setattr(services, "_waf_cookies", services._UNSET)


def _make_response(status_code: int, text: str = "", content: bytes = b""):
    return SimpleNamespace(status_code=status_code, text=text, content=content)


# ── _load_waf_cookies ─────────────────────────────────────────────────────────


def test_load_reads_disk_on_first_call(monkeypatch, tmp_path):
    """_UNSET triggers a single file read; result is stored in memory."""
    cookie_file = tmp_path / "waf_cookies.json"
    cookie_file.write_text(json.dumps({"aws-waf-token": "abc123"}), encoding="utf-8")
    _reset_cookie_state(monkeypatch, cookie_file)

    result = services._load_waf_cookies()

    assert result == {"aws-waf-token": "abc123"}
    # In-memory cache is now populated (no longer _UNSET)
    assert services._waf_cookies == {"aws-waf-token": "abc123"}


def test_load_uses_memory_on_subsequent_calls(monkeypatch, tmp_path):
    """Once the cache is warm the file is never read again."""
    cookie_file = tmp_path / "waf_cookies.json"
    # Pre-warm the in-memory cache — file contents deliberately differ
    monkeypatch.setattr(services, "_WAF_COOKIE_FILE", cookie_file)
    monkeypatch.setattr(services, "_waf_cookies", {"aws-waf-token": "from-memory"})
    cookie_file.write_text(json.dumps({"aws-waf-token": "from-disk"}), encoding="utf-8")

    result = services._load_waf_cookies()

    # Must return the in-memory value, not the disk value
    assert result == {"aws-waf-token": "from-memory"}


def test_load_returns_none_when_no_file(monkeypatch, tmp_path):
    """Missing file → returns None and sets _waf_cookies = None (not _UNSET)."""
    cookie_file = tmp_path / "waf_cookies.json"  # does not exist
    _reset_cookie_state(monkeypatch, cookie_file)

    result = services._load_waf_cookies()

    assert result is None
    assert services._waf_cookies is None


# ── _save_waf_cookies ─────────────────────────────────────────────────────────


def test_save_updates_memory_and_disk(monkeypatch, tmp_path):
    """_save_waf_cookies must update both the module variable and the file."""
    cookie_file = tmp_path / "waf_cookies.json"
    _reset_cookie_state(monkeypatch, cookie_file)
    new_cookies = {"aws-waf-token": "new-token"}

    services._save_waf_cookies(new_cookies)

    assert services._waf_cookies == new_cookies
    assert cookie_file.exists()
    assert json.loads(cookie_file.read_text(encoding="utf-8")) == new_cookies


# ── _delete_waf_cookie_file ───────────────────────────────────────────────────


def test_delete_clears_memory_and_removes_file(monkeypatch, tmp_path):
    """_delete_waf_cookie_file must set in-memory to None and unlink the file."""
    cookie_file = tmp_path / "waf_cookies.json"
    cookie_file.write_text(json.dumps({"aws-waf-token": "stale"}), encoding="utf-8")
    monkeypatch.setattr(services, "_WAF_COOKIE_FILE", cookie_file)
    monkeypatch.setattr(services, "_waf_cookies", {"aws-waf-token": "stale"})

    services._delete_waf_cookie_file()

    assert services._waf_cookies is None
    assert not cookie_file.exists()


# ── request_handler ───────────────────────────────────────────────────────────


def test_request_handler_sends_cached_cookies_on_200(monkeypatch, tmp_path):
    """Cached cookies are forwarded to niquests.get; a 200 leaves them intact."""
    cookie_file = tmp_path / "waf_cookies.json"
    cached = {"aws-waf-token": "valid-token"}
    monkeypatch.setattr(services, "_WAF_COOKIE_FILE", cookie_file)
    monkeypatch.setattr(services, "_waf_cookies", cached)

    received_cookies = {}

    def stub_get(url, headers=None, cookies=None, **kwargs):
        received_cookies.update(cookies or {})
        return _make_response(200)

    monkeypatch.setattr(services.niquests, "get", stub_get)

    resp = services.request_handler("https://www.imdb.com/title/tt0133093/reference")

    assert resp.status_code == 200
    assert received_cookies == cached
    # Cookies must still be in memory after a successful request
    assert services._waf_cookies == cached


def test_request_handler_refreshes_cookies_on_non_200(monkeypatch, tmp_path):
    """Non-200 → old cookies discarded, WAF solver called, new cookies saved & used."""
    cookie_file = tmp_path / "waf_cookies.json"
    monkeypatch.setattr(services, "_WAF_COOKIE_FILE", cookie_file)
    monkeypatch.setattr(services, "_waf_cookies", {"aws-waf-token": "old-token"})

    fresh_cookies = {"aws-waf-token": "fresh-token"}
    call_count = {"n": 0}

    def stub_get(url, headers=None, cookies=None, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return _make_response(403, text="forbidden")
        return _make_response(200)

    monkeypatch.setattr(services.niquests, "get", stub_get)
    monkeypatch.setattr(services, "get_cookies", lambda text, ua: fresh_cookies)

    resp = services.request_handler("https://www.imdb.com/title/tt0133093/reference")

    assert resp.status_code == 200
    assert call_count["n"] == 2  # initial request + retry
    assert services._waf_cookies == fresh_cookies
    assert cookie_file.exists()
    assert json.loads(cookie_file.read_text(encoding="utf-8")) == fresh_cookies


def test_request_handler_clears_cookies_when_retry_also_fails(monkeypatch, tmp_path):
    """If the retry after WAF solve still returns non-200, cookies are discarded."""
    cookie_file = tmp_path / "waf_cookies.json"
    monkeypatch.setattr(services, "_WAF_COOKIE_FILE", cookie_file)
    monkeypatch.setattr(services, "_waf_cookies", {"aws-waf-token": "old-token"})

    monkeypatch.setattr(
        services.niquests,
        "get",
        lambda *a, **kw: _make_response(403, text="still blocked"),
    )
    monkeypatch.setattr(
        services, "get_cookies", lambda text, ua: {"aws-waf-token": "attempted-token"}
    )

    resp = services.request_handler("https://www.imdb.com/title/tt0133093/reference")

    assert resp.status_code == 403
    assert services._waf_cookies is None
    assert not cookie_file.exists()
