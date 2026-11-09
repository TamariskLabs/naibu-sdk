"""Tests for the asynchronous client and resources."""

from __future__ import annotations

import httpx
import pytest
import respx

from naibu import AsyncNaibuClient
from naibu.exceptions import NaibuNotFoundError

BASE_URL = "https://api.test.naibu.com"


@respx.mock
async def test_async_retrieve() -> None:
    respx.get(f"{BASE_URL}/v1/customers/cus_1").mock(
        return_value=httpx.Response(200, json={"id": "cus_1", "name": "Acme"})
    )
    async with AsyncNaibuClient(api_key="sk_test", base_url=BASE_URL) as client:
        customer = await client.customers.retrieve("cus_1")
    assert customer.name == "Acme"


@respx.mock
async def test_async_not_found() -> None:
    respx.get(f"{BASE_URL}/v1/customers/missing").mock(
        return_value=httpx.Response(404, json={"error": {"message": "gone"}})
    )
    async with AsyncNaibuClient(api_key="sk_test", base_url=BASE_URL) as client:
        with pytest.raises(NaibuNotFoundError):
            await client.customers.retrieve("missing")


@respx.mock
async def test_async_list_autopaginates() -> None:
    respx.get(f"{BASE_URL}/v1/orders").mock(
        side_effect=[
            httpx.Response(
                200, json={"data": [{"id": "o1"}], "next_cursor": "n", "has_more": True}
            ),
            httpx.Response(200, json={"data": [{"id": "o2"}], "has_more": False}),
        ]
    )
    async with AsyncNaibuClient(api_key="sk_test", base_url=BASE_URL) as client:
        ids = [o.id async for o in client.orders.list()]
    assert ids == ["o1", "o2"]


@respx.mock
async def test_async_retries_on_503() -> None:
    route = respx.get(f"{BASE_URL}/v1/products/p1").mock(
        side_effect=[httpx.Response(503), httpx.Response(200, json={"id": "p1"})]
    )
    async with AsyncNaibuClient(api_key="sk_test", base_url=BASE_URL, max_retries=2) as client:
        product = await client.products.retrieve("p1")
    assert product.id == "p1"
    assert route.call_count == 2
