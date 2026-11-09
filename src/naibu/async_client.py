"""Asynchronous Naibu client."""

from __future__ import annotations

import asyncio
from types import TracebackType
from typing import Any, Mapping, Optional

import httpx

from ._internal.response import parse_json, raise_for_status
from ._internal.retry import backoff_delay, parse_retry_after, should_retry
from ._version import __version__
from .config import ClientConfig
from .exceptions import NaibuConnectionError, NaibuTimeoutError
from .resources.customers import AsyncCustomersResource
from .resources.invoices import AsyncInvoicesResource
from .resources.orders import AsyncOrdersResource
from .resources.products import AsyncProductsResource


class AsyncNaibuClient:
    """Asynchronous client for the Naibu ERP API.

    Example:
        >>> from naibu import AsyncNaibuClient
        >>> async with AsyncNaibuClient(api_key="sk_live_...") as client:
        ...     customer = await client.customers.retrieve("cus_123")

    See :class:`naibu.client.NaibuClient` for argument documentation.
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
        http_client: Optional[httpx.AsyncClient] = None,
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
        self._http = http_client or httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        )

        self.customers = AsyncCustomersResource(self)
        self.products = AsyncProductsResource(self)
        self.orders = AsyncOrdersResource(self)
        self.invoices = AsyncInvoicesResource(self)

    # -- lifecycle ---------------------------------------------------------
    async def close(self) -> None:
        """Close the underlying HTTP connection pool (if owned)."""
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self) -> "AsyncNaibuClient":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    # -- request plumbing --------------------------------------------------
    async def _build_headers(self, extra: Optional[Mapping[str, str]]) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": f"{self.config.user_agent}/{__version__}",
        }
        headers.update(self.config.default_headers)
        assert self.config.auth is not None
        headers.update(await self.config.auth.async_headers(client=self._http))
        if extra:
            headers.update(extra)
        return headers

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        """Send a request and return the parsed JSON body."""
        url = path if path.startswith("http") else f"/{path.lstrip('/')}"
        attempt = 0
        while True:
            try:
                response = await self._http.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=await self._build_headers(headers),
                )
            except httpx.TimeoutException as exc:
                if should_retry(
                    method=method,
                    status_code=408,
                    attempt=attempt,
                    max_retries=self.config.max_retries,
                ):
                    await asyncio.sleep(backoff_delay(attempt))
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
                await asyncio.sleep(backoff_delay(attempt, retry_after=retry_after))
                attempt += 1
                continue

            raise_for_status(response)
            return parse_json(response)
