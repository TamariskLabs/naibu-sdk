"""OAuth2 client-credentials example for the Naibu SDK.

Run with:
    NAIBU_CLIENT_ID=... NAIBU_CLIENT_SECRET=... \
    NAIBU_TOKEN_URL=https://auth.naibu.com/oauth/token \
    python examples/oauth2.py
"""

from __future__ import annotations

from naibu import NaibuClient, OAuth2ClientCredentials


def main() -> None:
    auth = OAuth2ClientCredentials(
        client_id="your-client-id",
        client_secret="your-client-secret",
        token_url="https://auth.naibu.com/oauth/token",
        scope="erp.read erp.write",
    )
    with NaibuClient(auth=auth) as client:
        order = client.orders.retrieve("ord_123")
        print(f"Order {order.id} status={order.status} total={order.total}")


if __name__ == "__main__":
    main()
