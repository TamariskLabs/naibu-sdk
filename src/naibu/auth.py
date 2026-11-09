"""Authentication providers for the Naibu SDK.

An :class:`AuthProvider` knows how to attach credentials to an outgoing request
and, where applicable, how to refresh them. Two providers are shipped:

* :class:`ApiKeyAuth` - static API key / bearer token.
* :class:`OAuth2ClientCredentials` - OAuth2 client-credentials grant with
  automatic token fetching and refresh.
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING, Mapping, Optional

from .exceptions import NaibuAuthenticationError, NaibuConfigError

if TYPE_CHECKING:
    import httpx


class AuthProvider:
    """Interface implemented by all authentication strategies."""

    def headers(self, *, client: "httpx.Client") -> Mapping[str, str]:
        """Return headers to attach to a synchronous request."""
        raise NotImplementedError

    async def async_headers(self, *, client: "httpx.AsyncClient") -> Mapping[str, str]:
        """Return headers to attach to an asynchronous request."""
        raise NotImplementedError


class ApiKeyAuth(AuthProvider):
    """Authenticate with a static API key sent as a bearer token.

    Args:
        api_key: The secret API key / token issued by Naibu.
        scheme: Authorization scheme to use. Defaults to ``"Bearer"``.
        header: Header name to place the credential in. Defaults to
            ``"Authorization"``.
    """

    def __init__(
        self,
        api_key: str,
        *,
        scheme: str = "Bearer",
        header: str = "Authorization",
    ) -> None:
        if not api_key:
            raise NaibuConfigError("api_key must be a non-empty string")
        self._api_key = api_key
        self._scheme = scheme
        self._header = header

    def _value(self) -> Mapping[str, str]:
        value = f"{self._scheme} {self._api_key}".strip() if self._scheme else self._api_key
        return {self._header: value}

    def headers(self, *, client: "httpx.Client") -> Mapping[str, str]:
        return self._value()

    async def async_headers(self, *, client: "httpx.AsyncClient") -> Mapping[str, str]:
        return self._value()


class OAuth2ClientCredentials(AuthProvider):
    """OAuth2 client-credentials grant.

    Fetches an access token from ``token_url`` and caches it until shortly
    before expiry, after which it transparently refreshes. Token fetching is
    thread-safe for the synchronous path.

    Args:
        client_id: OAuth2 client identifier.
        client_secret: OAuth2 client secret.
        token_url: Absolute URL of the token endpoint.
        scope: Optional space-delimited scope string.
        leeway: Seconds to subtract from the token lifetime to avoid using a
            token that is about to expire. Defaults to 30 seconds.
    """

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: Optional[str] = None,
        leeway: float = 30.0,
    ) -> None:
        if not client_id or not client_secret:
            raise NaibuConfigError("client_id and client_secret are required")
        if not token_url:
            raise NaibuConfigError("token_url is required")
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_url = token_url
        self._scope = scope
        self._leeway = leeway

        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = threading.Lock()

    def _payload(self) -> dict[str, str]:
        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        if self._scope:
            payload["scope"] = self._scope
        return payload

    def _is_valid(self) -> bool:
        return self._access_token is not None and time.monotonic() < self._expires_at

    def _store(self, data: Mapping[str, object]) -> str:
        token = data.get("access_token")
        if not isinstance(token, str):
            raise NaibuAuthenticationError(
                "token endpoint did not return an access_token", status_code=200, body=data
            )
        expires_in = float(data.get("expires_in", 3600))  # type: ignore[arg-type]
        self._access_token = token
        self._expires_at = time.monotonic() + max(expires_in - self._leeway, 0.0)
        return token

    def headers(self, *, client: "httpx.Client") -> Mapping[str, str]:
        with self._lock:
            if self._is_valid():
                assert self._access_token is not None
                return {"Authorization": f"Bearer {self._access_token}"}
            response = client.post(self._token_url, data=self._payload())
            if response.status_code >= 400:
                raise NaibuAuthenticationError(
                    "failed to obtain OAuth2 access token",
                    status_code=response.status_code,
                    body=_safe_json(response),
                )
            token = self._store(response.json())
            return {"Authorization": f"Bearer {token}"}

    async def async_headers(self, *, client: "httpx.AsyncClient") -> Mapping[str, str]:
        # A short critical section is acceptable; token fetches are infrequent.
        if self._is_valid():
            assert self._access_token is not None
            return {"Authorization": f"Bearer {self._access_token}"}
        response = await client.post(self._token_url, data=self._payload())
        if response.status_code >= 400:
            raise NaibuAuthenticationError(
                "failed to obtain OAuth2 access token",
                status_code=response.status_code,
                body=_safe_json(response),
            )
        token = self._store(response.json())
        return {"Authorization": f"Bearer {token}"}


def _safe_json(response: "httpx.Response") -> object:
    try:
        return response.json()
    except Exception:  # pragma: no cover - defensive
        return response.text
