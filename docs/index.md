# Naibu Python SDK

The official Python client for the **Naibu ERP** system.

- **Install:** `pip install naibu-sdk`
- **Import:** `import naibu`

```python
from naibu import NaibuClient

with NaibuClient(api_key="sk_live_...") as client:
    customer = client.customers.retrieve("cus_123")
    print(customer.name)
```

See the [Getting started](getting-started.md) guide to continue.
