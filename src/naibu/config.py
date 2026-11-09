"""Client configuration.

:class:`ClientConfig` centralizes every tunable knob and resolves values from
explicit arguments, then environment variables, then sensible defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from .auth import ApiKeyAuth, AuthProvider, OAuth2ClientCredentials
from .exceptions import NaibuConfigError

DEFAULT_BASE_URL = "https://api.naibu.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_USER_AGENT = "naibu-python"

ENV_API_KEY = "NAIBU_API_KEY"
ENV_BASE_URL = "NAIBU_BASE_URL"
ENV_CLIENT_ID = "NAIBU_CLIENT_ID"
ENV_CLIENT_SECRET = "NAIBU_CLIENT_SECRET"
ENV_TOKEN_URL = "NAIBU_TOKEN_URL"
ENV_SCOPE = "NAIBU_SCOPE"


@dataclass
class ClientConfig:
    """Resolved, immutable-ish configuration for a client instance.

    Prefer :meth:`resolve` over constructing this directly; it wires up
    environment-variable fallbacks and builds the appropriate auth provider.
    """

    base_url: str = DEFAULT_BASE_URL
    auth: Optional[AuthProvider] = None
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    user_agent: str = DEFAULT_USER_AGENT
    default_headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.base_url:
            raise NaibuConfigError("base_url must not be empty")
        self.base_url = self.base_url.rstrip("/")
        if self.timeout <= 0:
            raise NaibuConfigError("timeout must be positive")
        if self.max_retries < 0:
            raise NaibuConfigError("max_retries must be >= 0")

    @classmethod
    def resolve(
        cls,
        *,
        api_key: Optional[str] = None,
        auth: Optional[AuthProvider] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        user_agent: Optional[str] = None,
        default_headers: Optional[dict[str, str]] = None,
        # OAuth2 convenience parameters
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_url: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> "ClientConfig":
        """Build a config from explicit args, environment variables, and defaults.

        Exactly one authentication strategy must be resolvable. Precedence:

        1. An explicit ``auth`` provider.
        2. An ``api_key`` argument or ``NAIBU_API_KEY``.
        3. OAuth2 client-credentials args or their ``NAIBU_*`` env vars.
        """
        resolved_auth = _resolve_auth(
            auth=auth,
            api_key=api_key,
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scope=scope,
        )

        return cls(
            base_url=base_url or os.environ.get(ENV_BASE_URL) or DEFAULT_BASE_URL,
            auth=resolved_auth,
            timeout=DEFAULT_TIMEOUT if timeout is None else timeout,
            max_retries=DEFAULT_MAX_RETRIES if max_retries is None else max_retries,
            user_agent=user_agent or DEFAULT_USER_AGENT,
            default_headers=dict(default_headers or {}),
        )


def _resolve_auth(
    *,
    auth: Optional[AuthProvider],
    api_key: Optional[str],
    client_id: Optional[str],
    client_secret: Optional[str],
    token_url: Optional[str],
    scope: Optional[str],
) -> AuthProvider:
    if auth is not None:
        return auth

    api_key = api_key or os.environ.get(ENV_API_KEY)
    if api_key:
        return ApiKeyAuth(api_key)

    client_id = client_id or os.environ.get(ENV_CLIENT_ID)
    client_secret = client_secret or os.environ.get(ENV_CLIENT_SECRET)
    token_url = token_url or os.environ.get(ENV_TOKEN_URL)
    scope = scope or os.environ.get(ENV_SCOPE)
    if client_id and client_secret and token_url:
        return OAuth2ClientCredentials(
            client_id=client_id,
            client_secret=client_secret,
            token_url=token_url,
            scope=scope,
        )

    raise NaibuConfigError(
        "No credentials provided. Pass api_key=..., an auth=... provider, or "
        "client_id/client_secret/token_url (or set the corresponding NAIBU_* "
        "environment variables)."
    )
