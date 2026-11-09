---
description: How to write and run tests for the Naibu SDK.
applyTo: "tests/**/*.py"
---

# Naibu SDK — testing instructions

- Use **pytest**. Async tests are supported via `pytest-asyncio` (`asyncio_mode
  = "auto"`), so `async def test_...` works without a decorator.
- Mock HTTP with **respx** (`@respx.mock`). **Never** make real network calls in
  unit tests.
- When asserting request bodies, compare parsed JSON (`json.loads(...)`), not raw
  bytes — serialization whitespace is not stable.
- For every new resource, cover: success path, error mapping (e.g. 404 → the
  matching `NaibuError`), retry behavior on 5xx/429, and pagination.
- Mark tests that require a live Naibu API with `@pytest.mark.integration`; these
  are excluded by default (`pytest -m "not integration"`).
- Do not lower overall coverage. Add tests alongside behavior changes.

Run the suite:

```bash
pytest -m "not integration"
```
