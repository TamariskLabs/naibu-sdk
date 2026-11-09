"""Synchronous Naibu client."""

from __future__ import annotations

import time
from types import TracebackType
from typing import Any, Mapping, Optional

import httpx

from ._internal.response import parse_json, raise_for_status
from ._internal.retry import backoff_delay, parse_retry_after, should_retry
from ._version import __version__
from .config import ClientConfig
from .exceptions import NaibuConnectionError, NaibuTimeoutError
from .resources.customers import CustomersResource
from .resources.invoices import InvoicesResource
from .resources.orders import OrdersResource
from .resources.products import ProductsResource


class NaibuClient:
    """Synchronous client for the Naibu ERP API.

    Example:
        >>> from naibu import NaibuClient
        >>> with NaibuClient(api_key="sk_live_...") as client:
        ...     customer = client.customers.retrieve("cus_123")

    Args:
        api_key: Static API key / bearer token.
        auth: An explicit :class:`~naibu.auth.AuthProvider` (overrides api_key).
        base_url: API base URL. Defaults to the production endpoint.
        timeout: Per-request timeout in seconds.
        max_retries: Maximum automatic retries for transient failures.
        client_id, client_secret, token_url, scope: OAuth2 client-credentials
            parameters (used when no api_key/auth is supplied).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        auth: Optional[Any] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        user_agent: Optional[str] = None,
        default_headers: Optional[dict[str, str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_url: Optional[str] = None,
        scope: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.config = ClientConfig.resolve(
            api_key=api_key,
            auth=auth,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            user_agent=user_agent,
            default_headers=default_headers,
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scope=scope,
        )
        self._owns_http = http_client is None
        self._http = http_client or httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        )

        # Resource namespaces
        self.customers = CustomersResource(self)
        self.products = ProductsResource(self)
        self.orders = OrdersResource(self)
        self.invoices = InvoicesResource(self)

    # -- lifecycle ---------------------------------------------------------
    def close(self) -> None:
        """Close the underlying HTTP connection pool (if owned)."""
        if self._owns_http:
            self._http.close()

    def __enter__(self) -> "NaibuClient":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self.close()

    # -- request plumbing --------------------------------------------------
    def _build_headers(self, extra: Optional[Mapping[str, str]]) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": f"{self.config.user_agent}/{__version__}",
        }
        headers.update(self.config.default_headers)
        assert self.config.auth is not None
        headers.update(self.config.auth.headers(client=self._http))
        if extra:
            headers.update(extra)
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Send a request and return the parsed JSON body.

        Transient failures (429/5xx/connection errors) are retried with
        exponential backoff for idempotent methods.
        """
        url = path if path.startswith("http") else f"/{path.lstrip('/')}"
        attempt = 0
        while True:
            try:
                response = self._http.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=self._build_headers(headers),
                )
            except httpx.TimeoutException as exc:
                if should_retry(
                    method=method,
                    status_code=408,
                    attempt=attempt,
                    max_retries=self.config.max_retries,
                ):
                    time.sleep(backoff_delay(attempt))
                    attempt += 1
                    continue
                raise NaibuTimeoutError(f"request to {url} timed out") from exc
            except httpx.HTTPError as exc:
                raise NaibuConnectionError(f"failed to reach {url}: {exc}") from exc

            if should_retry(
                method=method,
                status_code=response.status_code,
                attempt=attempt,
                max_retries=self.config.max_retries,
            ):
                retry_after = parse_retry_after(response.headers.get("Retry-After"))
                time.sleep(backoff_delay(attempt, retry_after=retry_after))
                attempt += 1
                continue

            raise_for_status(response)
            return parse_json(response)
