# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository. Read this
before making changes. See also [RULES.md](RULES.md) for hard constraints and
[PLAN.md](PLAN.md) for the roadmap.

## What this project is

The **Naibu Python SDK** — the official client library for the Naibu ERP API.
It is distributed on PyPI as `naibu-sdk` and imported as `naibu`.

## Project layout

```
src/naibu/
├── __init__.py          # public exports (the stable API surface)
├── _version.py          # single source of version truth
├── client.py            # NaibuClient (sync) + request/retry loop
├── async_client.py      # AsyncNaibuClient (async) + request/retry loop
├── config.py            # ClientConfig.resolve() — arg/env/default resolution
├── auth.py              # ApiKeyAuth, OAuth2ClientCredentials
├── exceptions.py        # NaibuError hierarchy + status->exception mapping
├── pagination.py        # SyncPage / AsyncPage auto-pagination
├── py.typed             # PEP 561 typing marker
├── _internal/           # NON-public helpers (retry policy, response parsing)
├── models/              # dataclass models (base + domain models)
└── resources/           # one module per API collection (sync + async pair)
tests/                   # pytest suite (unit/ mocks HTTP via respx)
docs/                    # mkdocs documentation
examples/                # runnable usage examples
```

## Architecture conventions

- **Sync/async parity.** Every resource ships a `XxxResource` (sync) and an
  `AsyncXxxResource` (async) class with mirrored methods. Keep them in sync.
- **Thin resources.** Resources translate method calls into
  `self._client.request(method, path, ...)` and wrap the JSON result in a model.
  All transport, retry, and error logic lives in the clients and `_internal/`.
- **Typed exceptions.** Never raise bare `httpx` errors to users. Map them via
  `_internal/response.raise_for_status` and `exceptions.exception_for_status`.
- **Forward-compatible models.** `BaseModel.from_dict` captures unknown fields in
  `.extra` so new API fields never break deserialization.
- **No hidden network calls in `__init__`.** Constructing a client must not hit
  the network (OAuth token fetch happens lazily on first request).

## Build & validate (run these before finishing)

```bash
pip install -e ".[dev]"   # once
ruff check .              # lint
ruff format --check .     # formatting
mypy                      # strict static typing
pytest -m "not integration"  # tests + coverage
```

`make check` runs lint + typecheck + tests together.

## Adding a resource (recipe)

1. Add model(s) to `src/naibu/models/common.py` (or a new module) and export
   them from `models/__init__.py`.
2. Create `src/naibu/resources/<name>.py` with both sync and async classes,
   following `customers.py` as the template.
3. Register the namespaces in both `client.py` and `async_client.py`
   constructors.
4. Export any new public symbols from `src/naibu/__init__.py`.
5. Add unit tests under `tests/unit/` using `respx` (no real network).
6. Note the change in `CHANGELOG.md` under `## [Unreleased]`.

## Testing conventions

- Use `respx` to mock `httpx`; **never** make real network calls in unit tests.
- Mark tests needing a live API with `@pytest.mark.integration` (excluded by
  default via `-m "not integration"`).
- Cover success, error mapping, retries, and pagination for new resources.

## Python compatibility

- Must run on **Python 3.9+**.
- Use `from __future__ import annotations` in every module so annotations are
  lazy. Do **not** use PEP 604 (`X | Y`) or PEP 585 (`list[...]`) generics in
  runtime positions (type aliases, `cast(...)`, `isinstance`); use `typing`
  equivalents there.

## Definition of done

- Code is formatted, lint-clean, strictly typed, and tested.
- Public API changes are exported from `__init__.py` and documented.
- `CHANGELOG.md` updated. Sync and async variants both updated.
