# Authentication

The SDK supports two authentication strategies. Credentials may be passed
explicitly or resolved from environment variables.

## API key / bearer token

```python
from naibu import NaibuClient

client = NaibuClient(api_key="sk_live_...")
```

Or via the environment:

```bash
export NAIBU_API_KEY=sk_live_...
```

```python
client = NaibuClient()  # reads NAIBU_API_KEY
```

### Custom header or scheme

```python
from naibu import ApiKeyAuth, NaibuClient

auth = ApiKeyAuth("abc123", scheme="Token", header="X-Api-Key")
client = NaibuClient(auth=auth)
```

## OAuth2 client credentials

The SDK fetches an access token from your token endpoint and refreshes it
automatically before expiry.

```python
from naibu import NaibuClient

client = NaibuClient(
    client_id="...",
    client_secret="...",
    token_url="https://auth.naibu.com/oauth/token",
    scope="erp.read erp.write",
)
```

Environment variables:

| Variable              | Purpose              |
| --------------------- | -------------------- |
| `NAIBU_CLIENT_ID`     | OAuth2 client id     |
| `NAIBU_CLIENT_SECRET` | OAuth2 client secret |
| `NAIBU_TOKEN_URL`     | Token endpoint       |
| `NAIBU_SCOPE`         | Scope (optional)     |

## Resolution order

1. An explicit `auth=` provider.
2. `api_key=` / `NAIBU_API_KEY`.
3. OAuth2 client-credentials parameters / `NAIBU_*` env vars.
