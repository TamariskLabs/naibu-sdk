"""Order resource operations."""

from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from ..models.common import Order
from ..pagination import AsyncPage, SyncPage
from .base import AsyncResource, SyncResource

_PATH = "/v1/orders"


class OrdersResource(SyncResource):
    """Synchronous operations on orders."""

    def create(self, data: Mapping[str, Any]) -> Order:
        payload = self._client.request("POST", _PATH, json=dict(data))
        return Order.from_dict(payload)

    def retrieve(self, order_id: str) -> Order:
        payload = self._client.request("GET", f"{_PATH}/{order_id}")
        return Order.from_dict(payload)

    def cancel(self, order_id: str) -> Order:
        """Cancel an order."""
        payload = self._client.request("POST", f"{_PATH}/{order_id}/cancel")
        return Order.from_dict(payload)

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> SyncPage[Order]:
        def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast("Mapping[str, Any]", self._client.request("GET", _PATH, params=params))

        return SyncPage(fetch, Order.from_dict)


class AsyncOrdersResource(AsyncResource):
    """Asynchronous operations on orders."""

    async def create(self, data: Mapping[str, Any]) -> Order:
        payload = await self._client.request("POST", _PATH, json=dict(data))
        return Order.from_dict(payload)

    async def retrieve(self, order_id: str) -> Order:
        payload = await self._client.request("GET", f"{_PATH}/{order_id}")
        return Order.from_dict(payload)

    async def cancel(self, order_id: str) -> Order:
        payload = await self._client.request("POST", f"{_PATH}/{order_id}/cancel")
        return Order.from_dict(payload)

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> AsyncPage[Order]:
        async def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast(
                "Mapping[str, Any]", await self._client.request("GET", _PATH, params=params)
            )

        return AsyncPage(fetch, Order.from_dict)
