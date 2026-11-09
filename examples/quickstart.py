"""Synchronous quickstart for the Naibu SDK.

Run with:
    NAIBU_API_KEY=sk_live_... python examples/quickstart.py
"""

from __future__ import annotations

from naibu import NaibuAPIError, NaibuClient


def main() -> None:
    # Credentials are read from NAIBU_API_KEY if not passed explicitly.
    with NaibuClient() as client:
        try:
            # List the first page of customers.
            page = client.customers.list(limit=25).first_page()
            print(f"Fetched {len(page)} customers")

            # Iterate every product across all pages.
            for product in client.products.list():
                print(f"{product.sku}: {product.price} {product.currency}")

        except NaibuAPIError as exc:
            print(f"API error: {exc} (request_id={exc.request_id})")


if __name__ == "__main__":
    main()
