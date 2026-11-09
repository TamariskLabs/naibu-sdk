"""Exception hierarchy for the Naibu SDK.

All exceptions raised by the SDK derive from :class:`NaibuError`, so callers can
catch everything with a single ``except NaibuError``.
"""

from __future__ import annotations

from typing import Any, Optional


class NaibuError(Exception):
    """Base class for every error raised by the SDK."""


class NaibuConfigError(NaibuError):
    """Raised when the client is misconfigured (e.g. missing credentials)."""


class NaibuAPIError(NaibuError):
    """Base class for errors returned by the Naibu API.

    Attributes:
        status_code: HTTP status code of the response, if available.
        request_id: Value of the ``X-Request-Id`` response header, if present.
        code: Machine-readable error code returned by the API, if present.
        body: Parsed response body, if available.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        code: Optional[str] = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.code = code
        self.body = body

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"status={self.status_code}")
        if self.code:
            parts.append(f"code={self.code}")
        if self.request_id:
            parts.append(f"request_id={self.request_id}")
        return " ".join(parts)


class NaibuConnectionError(NaibuError):
    """Raised when the SDK cannot reach the API (network/DNS/TLS failure)."""


class NaibuTimeoutError(NaibuConnectionError):
    """Raised when a request exceeds the configured timeout."""


class NaibuAuthenticationError(NaibuAPIError):
    """HTTP 401 - credentials are missing or invalid."""


class NaibuPermissionError(NaibuAPIError):
    """HTTP 403 - authenticated but not authorized for the resource."""


class NaibuNotFoundError(NaibuAPIError):
    """HTTP 404 - the requested resource does not exist."""


class NaibuConflictError(NaibuAPIError):
    """HTTP 409 - the request conflicts with the current state."""


class NaibuValidationError(NaibuAPIError):
    """HTTP 422 - the request payload failed server-side validation."""


class NaibuRateLimitError(NaibuAPIError):
    """HTTP 429 - too many requests.

    Attributes:
        retry_after: Suggested wait time in seconds parsed from ``Retry-After``.
    """

    def __init__(self, *args: Any, retry_after: Optional[float] = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after


class NaibuServerError(NaibuAPIError):
    """HTTP 5xx - the server encountered an error."""


_STATUS_TO_EXCEPTION = {
    401: NaibuAuthenticationError,
    403: NaibuPermissionError,
    404: NaibuNotFoundError,
    409: NaibuConflictError,
    422: NaibuValidationError,
    429: NaibuRateLimitError,
}


def exception_for_status(status_code: int) -> type[NaibuAPIError]:
    """Return the most specific :class:`NaibuAPIError` subclass for a status."""
    if status_code in _STATUS_TO_EXCEPTION:
        return _STATUS_TO_EXCEPTION[status_code]
    if status_code >= 500:
        return NaibuServerError
    return NaibuAPIError
