# Getting started

## Install

```bash
pip install naibu-sdk
```

The distribution is named `naibu-sdk`; the import package is `naibu`.

## Create a client

```python
from naibu import NaibuClient

client = NaibuClient(api_key="sk_live_...")
```

Use the client as a context manager so connections are closed cleanly:

```python
with NaibuClient(api_key="sk_live_...") as client:
    ...
```

## Resources

Every resource exposes the same ergonomic methods:

```python
customer = client.customers.create({"name": "Acme"})
customer = client.customers.retrieve(customer.id)
customer = client.customers.update(customer.id, {"email": "ops@acme.example"})
client.customers.delete(customer.id)

for c in client.customers.list(limit=100):  # auto-paginates
    print(c.name)
```

## Async

```python
import asyncio
from naibu import AsyncNaibuClient


async def main():
    async with AsyncNaibuClient(api_key="sk_live_...") as client:
        async for product in client.products.list():
            print(product.sku)


asyncio.run(main())
```
