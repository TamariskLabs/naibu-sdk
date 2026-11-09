"""Asynchronous quickstart for the Naibu SDK.

Run with:
    NAIBU_API_KEY=sk_live_... python examples/async_quickstart.py
"""

from __future__ import annotations

import asyncio

from naibu import AsyncNaibuClient, NaibuAPIError


async def main() -> None:
    async with AsyncNaibuClient() as client:
        try:
            customer = await client.customers.create(
                {"name": "Acme Corp", "email": "ops@acme.example"}
            )
            print(f"Created customer {customer.id}")

            async for invoice in client.invoices.list(status="open"):
                print(f"Invoice {invoice.id}: {invoice.amount_due} due")

        except NaibuAPIError as exc:
            print(f"API error: {exc} (request_id={exc.request_id})")


if __name__ == "__main__":
    asyncio.run(main())
