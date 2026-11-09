# RULES.md

Hard rules and coding standards for the Naibu Python SDK. These are
non-negotiable constraints for both human and AI contributors. For broader
context see [AGENTS.md](AGENTS.md).

## 1. Security & secrets

- **Never** commit API keys, client secrets, tokens, or `.env` files.
- **Never** log credentials or full `Authorization` headers.
- Read secrets from parameters or `NAIBU_*` environment variables only.

## 2. Public API stability

- The public API is exactly what `src/naibu/__init__.py` exports. Anything under
  `naibu._internal` is private and may change without notice.
- Do not make breaking changes to public signatures without a major version bump
  and a `CHANGELOG.md` entry.
- New public symbols must be added to the relevant `__all__`.

## 3. Sync/async parity

- Every public resource operation must exist in **both** the sync and async
  variants with matching names and semantics. A change to one requires the same
  change to the other.

## 4. Typing

- The package is fully typed and must pass `mypy --strict` with no new errors.
- `disallow_untyped_defs` is on: every function/method needs complete
  annotations.
- Ship/maintain the `py.typed` marker.

## 5. Python 3.9+ compatibility

- Code must import and run on Python 3.9.
- Always `from __future__ import annotations` at the top of modules.
- No PEP 604 (`X | Y`) or PEP 585 (`list[...]`) generics in **runtime**
  positions (type aliases, `cast()`, base classes, `isinstance`). Use `typing`
  (`Optional`, `Union`, `List`, `Mapping`, ...) there.

## 6. Error handling

- Never leak raw `httpx` exceptions to callers. Wrap network failures in
  `NaibuConnectionError` / `NaibuTimeoutError` and HTTP errors via
  `raise_for_status`.
- All raised errors must derive from `NaibuError`.

## 7. HTTP & retries

- All requests go through `client.request()` — do not call `httpx` directly from
  resources.
- Only retry idempotent methods; honor `Retry-After`. Do not retry `POST`/`PATCH`.

## 8. Dependencies

- Runtime dependencies are limited to `httpx` (and `typing-extensions` on
  <3.11). Do **not** add new runtime dependencies without strong justification
  and sign-off. Dev-only tools go in the `dev` optional group.

## 9. Testing

- No real network calls in unit tests — mock with `respx`.
- New behavior must be covered by tests. Do not lower coverage.
- Live-API tests must be marked `@pytest.mark.integration`.

## 10. Quality gates (must pass before merge)

```bash
ruff check . && ruff format --check . && mypy && pytest -m "not integration"
```

## 11. Documentation & changelog

- Update `docs/` and `README.md` for user-facing changes.
- Add a `CHANGELOG.md` entry under `## [Unreleased]` for every notable change.
