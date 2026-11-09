"""Invoice resource operations."""

from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from ..models.common import Invoice
from ..pagination import AsyncPage, SyncPage
from .base import AsyncResource, SyncResource

_PATH = "/v1/invoices"


class InvoicesResource(SyncResource):
    """Synchronous operations on invoices."""

    def retrieve(self, invoice_id: str) -> Invoice:
        payload = self._client.request("GET", f"{_PATH}/{invoice_id}")
        return Invoice.from_dict(payload)

    def pay(self, invoice_id: str, data: Optional[Mapping[str, Any]] = None) -> Invoice:
        """Mark an invoice as paid."""
        payload = self._client.request(
            "POST", f"{_PATH}/{invoice_id}/pay", json=dict(data) if data else None
        )
        return Invoice.from_dict(payload)

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> SyncPage[Invoice]:
        def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast("Mapping[str, Any]", self._client.request("GET", _PATH, params=params))

        return SyncPage(fetch, Invoice.from_dict)


class AsyncInvoicesResource(AsyncResource):
    """Asynchronous operations on invoices."""

    async def retrieve(self, invoice_id: str) -> Invoice:
        payload = await self._client.request("GET", f"{_PATH}/{invoice_id}")
        return Invoice.from_dict(payload)

    async def pay(self, invoice_id: str, data: Optional[Mapping[str, Any]] = None) -> Invoice:
        payload = await self._client.request(
            "POST", f"{_PATH}/{invoice_id}/pay", json=dict(data) if data else None
        )
        return Invoice.from_dict(payload)

    def list(self, *, limit: Optional[int] = None, **filters: Any) -> AsyncPage[Invoice]:
        async def fetch(cursor: Optional[str]) -> Mapping[str, Any]:
            params: dict[str, Any] = {**filters}
            if limit is not None:
                params["limit"] = limit
            if cursor is not None:
                params["cursor"] = cursor
            return cast(
                "Mapping[str, Any]", await self._client.request("GET", _PATH, params=params)
            )

        return AsyncPage(fetch, Invoice.from_dict)
