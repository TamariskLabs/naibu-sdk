"""Retry policy: decide whether to retry and how long to wait."""

from __future__ import annotations

import random
from typing import Optional

# Methods that are safe to retry automatically.
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})

# Status codes worth retrying (transient server/limit conditions).
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})

_BASE_DELAY = 0.5
_MAX_DELAY = 30.0


def should_retry(*, method: str, status_code: int, attempt: int, max_retries: int) -> bool:
    """Return ``True`` if another attempt should be made."""
    if attempt >= max_retries:
        return False
    if method.upper() not in IDEMPOTENT_METHODS:
        return False
    return status_code in RETRYABLE_STATUS


def backoff_delay(attempt: int, *, retry_after: Optional[float] = None) -> float:
    """Compute the delay before the next attempt.

    Honors a server-provided ``Retry-After`` when present, otherwise uses
    exponential backoff with full jitter.

    Args:
        attempt: Zero-based index of the attempt that just failed.
        retry_after: Optional server hint in seconds.
    """
    if retry_after is not None and retry_after >= 0:
        return min(retry_after, _MAX_DELAY)
    exponential = min(_BASE_DELAY * (2**attempt), _MAX_DELAY)
    return random.uniform(0, exponential)


def parse_retry_after(value: Optional[str]) -> Optional[float]:
    """Parse a ``Retry-After`` header value expressed in seconds."""
    if not value:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
