"""Tests for authentication providers."""

from __future__ import annotations

import httpx
import pytest
import respx

from naibu.auth import ApiKeyAuth, OAuth2ClientCredentials
from naibu.exceptions import NaibuAuthenticationError, NaibuConfigError

TOKEN_URL = "https://auth.test/token"


def test_api_key_header() -> None:
    auth = ApiKeyAuth("sk_test")
    with httpx.Client() as client:
        assert auth.headers(client=client) == {"Authorization": "Bearer sk_test"}


def test_api_key_custom_scheme_and_header() -> None:
    auth = ApiKeyAuth("abc", scheme="Token", header="X-Api-Key")
    with httpx.Client() as client:
        assert auth.headers(client=client) == {"X-Api-Key": "Token abc"}


def test_api_key_empty_rejected() -> None:
    with pytest.raises(NaibuConfigError):
        ApiKeyAuth("")


@respx.mock
def test_oauth2_fetches_and_caches_token() -> None:
    route = respx.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok_1", "expires_in": 3600})
    )
    auth = OAuth2ClientCredentials(
        client_id="id", client_secret="secret", token_url=TOKEN_URL, scope="read"
    )
    with httpx.Client() as client:
        first = auth.headers(client=client)
        second = auth.headers(client=client)
    assert first == {"Authorization": "Bearer tok_1"}
    assert second == first
    assert route.call_count == 1  # cached


@respx.mock
def test_oauth2_error_raises() -> None:
    respx.post(TOKEN_URL).mock(return_value=httpx.Response(401, json={"error": "bad"}))
    auth = OAuth2ClientCredentials(client_id="id", client_secret="secret", token_url=TOKEN_URL)
    with httpx.Client() as client, pytest.raises(NaibuAuthenticationError):
        auth.headers(client=client)


@respx.mock
def test_oauth2_missing_token_raises() -> None:
    respx.post(TOKEN_URL).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
    auth = OAuth2ClientCredentials(client_id="id", client_secret="secret", token_url=TOKEN_URL)
    with httpx.Client() as client, pytest.raises(NaibuAuthenticationError):
        auth.headers(client=client)


@respx.mock
async def test_oauth2_async() -> None:
    respx.post(TOKEN_URL).mock(
        return_value=httpx.Response(200, json={"access_token": "tok_a", "expires_in": 3600})
    )
    auth = OAuth2ClientCredentials(client_id="id", client_secret="secret", token_url=TOKEN_URL)
    async with httpx.AsyncClient() as client:
        headers = await auth.async_headers(client=client)
    assert headers == {"Authorization": "Bearer tok_a"}


def test_oauth2_requires_fields() -> None:
    with pytest.raises(NaibuConfigError):
        OAuth2ClientCredentials(client_id="", client_secret="s", token_url=TOKEN_URL)
    with pytest.raises(NaibuConfigError):
        OAuth2ClientCredentials(client_id="i", client_secret="s", token_url="")
