"""Customer resource operations."""

from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from ..models.common import Customer
from ..pagination import AsyncPage, SyncPage
from .base import AsyncResource, SyncResource

_PATH = "/v1/customers"


class CustomersResource(SyncResource):
    """Synchronous operations on customers."""

    def create(self, data: Mapping[str, Any]) -> Customer:
        """Create a customer."""
        payload = self._client.request("POST", _PATH, json=dict(data))
        return Customer.from_dict(payload)

    def retrieve(self, customer_id: str) -> Customer:
        """Retrieve a single customer by id."""
        payload = self._client.request("GET", f"{_PATH}/{customer_id}")
        return Customer.from_dict(payload)

    def update(self, customer_id: str, data: Mapping[str, Any]) -> Customer:
        """Update a customer."""
        payload = self._client.request("PATCH", f"{_PATH}/{customer_id}", json=dict(data))
        return Customer.from_dict(payload)

    def delete(self, customer_id: str) -> None:
        """Delete a customer."""
        self._client.request("DELETE", f"{_PATH}/{customer_id}")

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> SyncPage[Customer]:
        """List customers, auto-paginating across all pages."""

        def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast("Mapping[str, Any]", self._client.request("GET", _PATH, params=params))

        return SyncPage(fetch, Customer.from_dict)


class AsyncCustomersResource(AsyncResource):
    """Asynchronous operations on customers."""

    async def create(self, data: Mapping[str, Any]) -> Customer:
        payload = await self._client.request("POST", _PATH, json=dict(data))
        return Customer.from_dict(payload)

    async def retrieve(self, customer_id: str) -> Customer:
        payload = await self._client.request("GET", f"{_PATH}/{customer_id}")
        return Customer.from_dict(payload)

    async def update(self, customer_id: str, data: Mapping[str, Any]) -> Customer:
        payload = await self._client.request("PATCH", f"{_PATH}/{customer_id}", json=dict(data))
        return Customer.from_dict(payload)

    async def delete(self, customer_id: str) -> None:
        await self._client.request("DELETE", f"{_PATH}/{customer_id}")

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> AsyncPage[Customer]:
        async def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast(
                "Mapping[str, Any]", await self._client.request("GET", _PATH, params=params)
            )

        return AsyncPage(fetch, Customer.from_dict)
