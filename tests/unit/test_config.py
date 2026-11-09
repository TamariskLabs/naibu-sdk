"""Tests for configuration resolution."""

from __future__ import annotations

import pytest

from naibu.auth import ApiKeyAuth, OAuth2ClientCredentials
from naibu.config import ClientConfig
from naibu.exceptions import NaibuConfigError


def test_resolve_with_api_key() -> None:
    config = ClientConfig.resolve(api_key="sk_test")
    assert isinstance(config.auth, ApiKeyAuth)
    assert config.base_url == "https://api.naibu.com"


def test_resolve_strips_trailing_slash() -> None:
    config = ClientConfig.resolve(api_key="sk_test", base_url="https://x.test/")
    assert config.base_url == "https://x.test"


def test_resolve_oauth2() -> None:
    config = ClientConfig.resolve(
        client_id="id", client_secret="secret", token_url="https://x.test/token"
    )
    assert isinstance(config.auth, OAuth2ClientCredentials)


def test_resolve_prefers_explicit_auth() -> None:
    auth = ApiKeyAuth("explicit")
    config = ClientConfig.resolve(auth=auth, api_key="ignored")
    assert config.auth is auth


def test_resolve_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ("NAIBU_API_KEY", "NAIBU_CLIENT_ID", "NAIBU_CLIENT_SECRET", "NAIBU_TOKEN_URL"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(NaibuConfigError):
        ClientConfig.resolve()


def test_resolve_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NAIBU_API_KEY", "env_key")
    monkeypatch.setenv("NAIBU_BASE_URL", "https://env.test")
    config = ClientConfig.resolve()
    assert isinstance(config.auth, ApiKeyAuth)
    assert config.base_url == "https://env.test"


def test_invalid_timeout() -> None:
    with pytest.raises(NaibuConfigError):
        ClientConfig(base_url="https://x.test", auth=ApiKeyAuth("k"), timeout=0)


def test_invalid_max_retries() -> None:
    with pytest.raises(NaibuConfigError):
        ClientConfig(base_url="https://x.test", auth=ApiKeyAuth("k"), max_retries=-1)
