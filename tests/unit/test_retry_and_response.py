"""Tests for retry policy and response handling."""

from __future__ import annotations

import httpx
import pytest

from naibu._internal.response import parse_json, raise_for_status
from naibu._internal.retry import (
    backoff_delay,
    parse_retry_after,
    should_retry,
)
from naibu.exceptions import (
    NaibuNotFoundError,
    NaibuRateLimitError,
    NaibuServerError,
    NaibuValidationError,
)


@pytest.mark.parametrize(
    ("method", "status", "attempt", "expected"),
    [
        ("GET", 503, 0, True),
        ("GET", 500, 2, True),
        ("GET", 404, 0, False),
        ("POST", 503, 0, False),  # non-idempotent
        ("GET", 503, 3, False),  # exhausted
    ],
)
def test_should_retry(method: str, status: int, attempt: int, expected: bool) -> None:
    assert (
        should_retry(method=method, status_code=status, attempt=attempt, max_retries=3) is expected
    )


def test_backoff_honors_retry_after() -> None:
    assert backoff_delay(0, retry_after=2.0) == 2.0


def test_backoff_jitter_bounded() -> None:
    for attempt in range(5):
        delay = backoff_delay(attempt)
        assert 0 <= delay <= 30.0


def test_parse_retry_after() -> None:
    assert parse_retry_after("5") == 5.0
    assert parse_retry_after(None) is None
    assert parse_retry_after("not-a-number") is None


def test_parse_json_empty() -> None:
    assert parse_json(httpx.Response(204)) is None


def test_raise_for_status_ok() -> None:
    raise_for_status(httpx.Response(200, json={"ok": True}))


def test_raise_for_status_404() -> None:
    resp = httpx.Response(404, json={"error": {"message": "nope", "code": "not_found"}})
    with pytest.raises(NaibuNotFoundError) as exc:
        raise_for_status(resp)
    assert exc.value.code == "not_found"
    assert exc.value.status_code == 404


def test_raise_for_status_422() -> None:
    resp = httpx.Response(422, json={"error": {"detail": "invalid"}})
    with pytest.raises(NaibuValidationError):
        raise_for_status(resp)


def test_raise_for_status_429_retry_after() -> None:
    resp = httpx.Response(429, headers={"Retry-After": "7"}, json={"error": "slow down"})
    with pytest.raises(NaibuRateLimitError) as exc:
        raise_for_status(resp)
    assert exc.value.retry_after == 7.0


def test_raise_for_status_500() -> None:
    resp = httpx.Response(500, text="boom")
    with pytest.raises(NaibuServerError):
        raise_for_status(resp)
