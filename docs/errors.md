# Error handling

All SDK errors inherit from `NaibuError`.

```python
from naibu import (
    NaibuClient,
    NaibuError,
    NaibuAPIError,
    NaibuAuthenticationError,
    NaibuNotFoundError,
    NaibuRateLimitError,
)

client = NaibuClient(api_key="sk_live_...")

try:
    client.customers.retrieve("missing")
except NaibuNotFoundError:
    ...  # HTTP 404
except NaibuRateLimitError as exc:
    print("retry after", exc.retry_after)
except NaibuAPIError as exc:
    print(exc.status_code, exc.code, exc.request_id)
except NaibuError:
    ...  # catch-all for anything the SDK raises
```

## Exception hierarchy

| Exception                   | Trigger                         |
| --------------------------- | ------------------------------- |
| `NaibuConfigError`          | Misconfiguration (no creds)     |
| `NaibuConnectionError`      | Network/DNS/TLS failure         |
| `NaibuTimeoutError`         | Request timed out               |
| `NaibuAuthenticationError`  | HTTP 401                        |
| `NaibuPermissionError`      | HTTP 403                        |
| `NaibuNotFoundError`        | HTTP 404                        |
| `NaibuConflictError`        | HTTP 409                        |
| `NaibuValidationError`      | HTTP 422                        |
| `NaibuRateLimitError`       | HTTP 429 (has `retry_after`)    |
| `NaibuServerError`          | HTTP 5xx                        |

## Retries

Idempotent requests (`GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`) are retried
automatically on `408`, `429`, and `5xx` responses using exponential backoff
with jitter, honoring `Retry-After` when present. Tune with `max_retries`.
