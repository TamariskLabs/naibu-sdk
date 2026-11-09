# Contributing to the Naibu Python SDK

Thanks for your interest in improving the SDK! This document describes the
local workflow and the conventions we follow.

## Development setup

```bash
git clone https://github.com/TamariskLabs/naibu-sdk.git
cd naibu-sdk
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
pre-commit install   # optional but recommended
```

## Quality gates

Every change must pass the same checks CI runs:

```bash
ruff check .        # lint
ruff format --check .  # formatting
mypy                # static types (strict)
pytest              # tests + coverage
```

Or run everything via the Makefile:

```bash
make check
```

## Conventions

- **Code style:** enforced by `ruff` (lint + format). Line length 100.
- **Typing:** the package is fully typed and checked under `mypy --strict`.
  Public functions must have complete annotations.
- **Python support:** code must run on Python 3.9+. Avoid runtime use of
  PEP 604 unions (`X | Y`) and PEP 585 generics outside `from __future__ import
  annotations` contexts.
- **Tests:** add/extend tests under `tests/unit`. Use `respx` to mock HTTP; do
  not make real network calls. Mark live-API tests with `@pytest.mark.integration`.
- **Commits:** write clear, imperative commit messages. Conventional Commits
  (`feat:`, `fix:`, `docs:`, ...) are encouraged.
- **Changelog:** add a note under `## [Unreleased]` in `CHANGELOG.md`.

## Adding a new resource

1. Add the model(s) in `src/naibu/models/`.
2. Create `src/naibu/resources/<name>.py` with a `SyncResource` and an
   `AsyncResource` subclass mirroring each other.
3. Register the namespace on both `NaibuClient` and `AsyncNaibuClient`.
4. Export new public names from the relevant `__init__.py`.
5. Add tests covering CRUD, error mapping, and pagination.

## Pull requests

- Keep PRs focused and small where possible.
- Ensure `make check` passes locally.
- Update docs and the changelog alongside code changes.
