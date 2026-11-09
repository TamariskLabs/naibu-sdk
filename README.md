# Naibu Python SDK

[![CI](https://github.com/TamariskLabs/naibu-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/TamariskLabs/naibu-sdk/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

The official Python SDK for the **Naibu ERP** system. It provides typed,
ergonomic access to the Naibu API with both **synchronous** and **asynchronous**
clients, automatic retries, typed exceptions, and transparent pagination.

> **Package naming:** install the distribution `naibu-sdk`; import the package as
> `naibu`.
>
> ```bash
> pip install naibu-sdk
> ```
> ```python
> import naibu
> ```

## Features

- 🔄 **Sync & async** clients sharing the same API surface
- 🔐 **Pluggable auth**: API key / bearer token and OAuth2 client-credentials
  (with automatic token refresh)
- ♻️ **Automatic retries** with exponential backoff + jitter for transient errors
- 🧯 **Typed exceptions** mapped from HTTP status codes
- 📄 **Auto-pagination** — iterate every record without managing cursors
- 🏷️ **Fully typed** (ships `py.typed`), zero heavyweight dependencies (just `httpx`)

## Installation

```bash
pip install naibu-sdk
```

## Quickstart

### Synchronous

```python
from naibu import NaibuClient

with NaibuClient(api_key="sk_live_...") as client:
    # Retrieve a single record
    customer = client.customers.retrieve("cus_123")
    print(customer.name)

    # Create a record
    order = client.orders.create({"customer_id": customer.id, "lines": []})

    # Auto-paginate across all pages
    for product in client.products.list(limit=100):
        print(product.sku, product.price)
```

### Asynchronous

```python
import asyncio
from naibu import AsyncNaibuClient


async def main() -> None:
    async with AsyncNaibuClient(api_key="sk_live_...") as client:
        customer = await client.customers.retrieve("cus_123")
        async for invoice in client.invoices.list(status="open"):
            print(invoice.id, invoice.amount_due)


asyncio.run(main())
```

## Authentication

Credentials can be passed explicitly or read from environment variables.

### API key / bearer token

```python
client = NaibuClient(api_key="sk_live_...")
# or: export NAIBU_API_KEY=sk_live_...
client = NaibuClient()
```

### OAuth2 client credentials

```python
client = NaibuClient(
    client_id="...",
    client_secret="...",
    token_url="https://auth.naibu.com/oauth/token",
    scope="erp.read erp.write",
)
# or set NAIBU_CLIENT_ID / NAIBU_CLIENT_SECRET / NAIBU_TOKEN_URL / NAIBU_SCOPE
```

### Environment variables

| Variable             | Purpose                              |
| -------------------- | ------------------------------------ |
| `NAIBU_API_KEY`      | API key / bearer token               |
| `NAIBU_CLIENT_ID`    | OAuth2 client id                     |
| `NAIBU_CLIENT_SECRET`| OAuth2 client secret                 |
| `NAIBU_TOKEN_URL`    | OAuth2 token endpoint                |
| `NAIBU_SCOPE`        | OAuth2 scope (optional)              |
| `NAIBU_BASE_URL`     | Override the API base URL (optional) |

## Error handling

All errors derive from `NaibuError`:

```python
from naibu import NaibuClient, NaibuNotFoundError, NaibuRateLimitError, NaibuAPIError

try:
    client.customers.retrieve("missing")
except NaibuNotFoundError:
    ...  # 404
except NaibuRateLimitError as e:
    print("retry after", e.retry_after)
except NaibuAPIError as e:
    print(e.status_code, e.code, e.request_id)
```

## Configuration

| Option          | Default                   | Description                       |
| --------------- | ------------------------- | --------------------------------- |
| `base_url`      | `https://api.naibu.com`   | API base URL                      |
| `timeout`       | `30.0`                    | Per-request timeout (seconds)     |
| `max_retries`   | `3`                       | Retries for transient failures    |
| `default_headers` | `{}`                    | Headers added to every request    |
| `http_client`   | managed internally        | Bring your own `httpx` client     |

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
ruff check .
mypy
pytest
```

## License

[MIT](LICENSE) © Tamarisk Labs
