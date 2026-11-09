"""Tests for the synchronous client and resources."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from naibu import NaibuClient
from naibu.exceptions import NaibuNotFoundError, NaibuServerError, NaibuTimeoutError

BASE_URL = "https://api.test.naibu.com"


@pytest.fixture
def client() -> NaibuClient:
    return NaibuClient(api_key="sk_test", base_url=BASE_URL, max_retries=2)


@respx.mock
def test_retrieve_customer(client: NaibuClient) -> None:
    respx.get(f"{BASE_URL}/v1/customers/cus_1").mock(
        return_value=httpx.Response(200, json={"id": "cus_1", "name": "Acme"})
    )
    customer = client.customers.retrieve("cus_1")
    assert customer.id == "cus_1"
    assert customer.name == "Acme"


@respx.mock
def test_create_customer_sends_json(client: NaibuClient) -> None:
    route = respx.post(f"{BASE_URL}/v1/customers").mock(
        return_value=httpx.Response(201, json={"id": "cus_2", "name": "New"})
    )
    client.customers.create({"name": "New"})
    assert route.called
    assert json.loads(route.calls.last.request.content) == {"name": "New"}


@respx.mock
def test_auth_header_sent(client: NaibuClient) -> None:
    route = respx.get(f"{BASE_URL}/v1/customers/cus_1").mock(
        return_value=httpx.Response(200, json={"id": "cus_1"})
    )
    client.customers.retrieve("cus_1")
    assert route.calls.last.request.headers["Authorization"] == "Bearer sk_test"


@respx.mock
def test_not_found_raises(client: NaibuClient) -> None:
    respx.get(f"{BASE_URL}/v1/customers/missing").mock(
        return_value=httpx.Response(404, json={"error": {"message": "gone"}})
    )
    with pytest.raises(NaibuNotFoundError):
        client.customers.retrieve("missing")


@respx.mock
def test_retries_on_503_then_succeeds(client: NaibuClient) -> None:
    route = respx.get(f"{BASE_URL}/v1/customers/cus_1").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json={"id": "cus_1"}),
        ]
    )
    customer = client.customers.retrieve("cus_1")
    assert customer.id == "cus_1"
    assert route.call_count == 2


@respx.mock
def test_retries_exhausted_raises(client: NaibuClient) -> None:
    respx.get(f"{BASE_URL}/v1/customers/cus_1").mock(return_value=httpx.Response(500))
    with pytest.raises(NaibuServerError):
        client.customers.retrieve("cus_1")


@respx.mock
def test_timeout_raises(client: NaibuClient) -> None:
    respx.get(f"{BASE_URL}/v1/customers/cus_1").mock(
        side_effect=httpx.TimeoutException("timed out")
    )
    with pytest.raises(NaibuTimeoutError):
        client.customers.retrieve("cus_1")


@respx.mock
def test_list_autopaginates(client: NaibuClient) -> None:
    respx.get(f"{BASE_URL}/v1/customers").mock(
        side_effect=[
            httpx.Response(
                200,
                json={"data": [{"id": "c1"}], "next_cursor": "abc", "has_more": True},
            ),
            httpx.Response(
                200,
                json={"data": [{"id": "c2"}], "has_more": False},
            ),
        ]
    )
    ids = [c.id for c in client.customers.list()]
    assert ids == ["c1", "c2"]


@respx.mock
def test_context_manager_closes() -> None:
    respx.get(f"{BASE_URL}/v1/customers/cus_1").mock(
        return_value=httpx.Response(200, json={"id": "cus_1"})
    )
    with NaibuClient(api_key="sk_test", base_url=BASE_URL) as c:
        assert c.customers.retrieve("cus_1").id == "cus_1"
