---
description: Core conventions for all Python code in the Naibu SDK.
applyTo: "src/naibu/**/*.py"
---

# Naibu SDK — Python coding instructions

You are working on the **Naibu Python SDK** (`pip install naibu-sdk`, imported as
`naibu`). Follow these rules for any code under `src/naibu/`.

## Non-negotiables

- Start every module with `from __future__ import annotations`.
- Support **Python 3.9+**. Do NOT use PEP 604 (`X | Y`) or PEP 585 (`list[...]`)
  in runtime positions (type aliases, `cast(...)`, base classes, `isinstance`).
  Use `typing.Optional`, `typing.Union`, `typing.Mapping`, etc. there. In pure
  annotation positions they are fine because annotations are lazy.
- All code must pass `mypy --strict` — fully annotate every function.
- Only `httpx` is allowed as a runtime dependency. Do not add others.

## Architecture

- **Resources are thin.** They call `self._client.request(method, path, ...)` and
  wrap the JSON result in a model. No direct `httpx` usage in resources.
- **Maintain sync/async parity.** Any change to a `XxxResource` must be mirrored
  in `AsyncXxxResource`, and vice versa.
- **Errors:** never surface raw `httpx` exceptions. Use the mappers in
  `_internal/response.py`; all SDK errors derive from `NaibuError`.
- **Models:** subclass `BaseModel`, use `Optional[...]` dataclass fields with
  `None` defaults, and rely on `from_dict`/`to_dict`. Unknown API fields are
  preserved in `.extra`.
- **Public API** = whatever `src/naibu/__init__.py` exports. Add new public
  names to the relevant `__all__`. Anything in `_internal/` is private.

## Style

- Line length 100; formatting via `ruff format`.
- Google-style docstrings on public classes/methods.
- Only comment code that genuinely needs clarification.
