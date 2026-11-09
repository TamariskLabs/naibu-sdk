"""Translate HTTP responses into parsed data or typed exceptions."""

from __future__ import annotations

from typing import Any

import httpx

from ..exceptions import (
    NaibuRateLimitError,
    exception_for_status,
)
from .retry import parse_retry_after


def parse_json(response: httpx.Response) -> Any:
    """Return the decoded JSON body, or ``None`` for empty responses."""
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text


def raise_for_status(response: httpx.Response) -> None:
    """Raise a typed :class:`NaibuAPIError` for 4xx/5xx responses."""
    if response.status_code < 400:
        return

    body = parse_json(response)
    message, code = _extract_error(body, response.status_code)
    request_id = response.headers.get("X-Request-Id")
    exc_cls = exception_for_status(response.status_code)

    if exc_cls is NaibuRateLimitError:
        raise NaibuRateLimitError(
            message,
            status_code=response.status_code,
            request_id=request_id,
            code=code,
            body=body,
            retry_after=parse_retry_after(response.headers.get("Retry-After")),
        )

    raise exc_cls(
        message,
        status_code=response.status_code,
        request_id=request_id,
        code=code,
        body=body,
    )


def _extract_error(body: Any, status_code: int) -> tuple[str, str | None]:
    """Pull a human message and machine code out of a (variably shaped) body."""
    default = f"Naibu API request failed with status {status_code}"
    if isinstance(body, dict):
        error = body.get("error", body)
        if isinstance(error, dict):
            message = error.get("message") or error.get("detail") or default
            code = error.get("code") or error.get("type")
            return str(message), (str(code) if code is not None else None)
        if isinstance(error, str):
            return error, None
    return default, None
