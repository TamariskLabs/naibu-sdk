"""Product resource operations."""

from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from ..models.common import Product
from ..pagination import AsyncPage, SyncPage
from .base import AsyncResource, SyncResource

_PATH = "/v1/products"


class ProductsResource(SyncResource):
    """Synchronous operations on products."""

    def create(self, data: Mapping[str, Any]) -> Product:
        payload = self._client.request("POST", _PATH, json=dict(data))
        return Product.from_dict(payload)

    def retrieve(self, product_id: str) -> Product:
        payload = self._client.request("GET", f"{_PATH}/{product_id}")
        return Product.from_dict(payload)

    def update(self, product_id: str, data: Mapping[str, Any]) -> Product:
        payload = self._client.request("PATCH", f"{_PATH}/{product_id}", json=dict(data))
        return Product.from_dict(payload)

    def delete(self, product_id: str) -> None:
        self._client.request("DELETE", f"{_PATH}/{product_id}")

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> SyncPage[Product]:
        def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast("Mapping[str, Any]", self._client.request("GET", _PATH, params=params))

        return SyncPage(fetch, Product.from_dict)


class AsyncProductsResource(AsyncResource):
    """Asynchronous operations on products."""

    async def create(self, data: Mapping[str, Any]) -> Product:
        payload = await self._client.request("POST", _PATH, json=dict(data))
        return Product.from_dict(payload)

    async def retrieve(self, product_id: str) -> Product:
        payload = await self._client.request("GET", f"{_PATH}/{product_id}")
        return Product.from_dict(payload)

    async def update(self, product_id: str, data: Mapping[str, Any]) -> Product:
        payload = await self._client.request("PATCH", f"{_PATH}/{product_id}", json=dict(data))
        return Product.from_dict(payload)

    async def delete(self, product_id: str) -> None:
        await self._client.request("DELETE", f"{_PATH}/{product_id}")

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> AsyncPage[Product]:
        async def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast(
                "Mapping[str, Any]", await self._client.request("GET", _PATH, params=params)
            )

        return AsyncPage(fetch, Product.from_dict)
