# PLAN.md

Development plan and roadmap for the Naibu Python SDK. This is a living document
— update it as milestones are completed. See [AGENTS.md](AGENTS.md) for how to
work in the repo and [RULES.md](RULES.md) for the hard constraints.

## Vision

A production-grade, fully typed Python SDK that makes integrating with the Naibu
ERP API effortless: ergonomic sync and async clients, robust error handling,
automatic retries and pagination, and excellent docs.

## Current status

**v0.1.0 — scaffold complete.** Core architecture is in place with example
resources (customers, products, orders, invoices), both client flavors, auth,
retries, pagination, tests, CI, and docs.

> ⚠️ The resource set and models are **illustrative**. They demonstrate the
> conventions and must be replaced/extended to match the real Naibu API.

## Milestones

### M1 — Foundation ✅ (done)
- [x] `src/` layout, packaging (hatch), tooling (ruff, mypy, pytest)
- [x] Sync + async clients with retry/backoff
- [x] API key + OAuth2 client-credentials auth
- [x] Typed exception hierarchy
- [x] Dataclass models + auto-pagination
- [x] Unit tests, CI matrix, docs scaffold, agentic dev files

### M2 — Real API surface
- [ ] Obtain the Naibu OpenAPI spec (or endpoint catalog)
- [ ] Replace example resources/models with the real domain
      (e.g. accounts, inventory, purchase orders, GL, payroll — TBD)
- [ ] Decide between hand-written vs. code-generated models
- [ ] Idempotency-key support for create/mutating endpoints
- [ ] Webhook signature verification helper (if applicable)

### M3 — Hardening
- [ ] Configurable connection pooling / proxies / custom transports
- [ ] Structured logging hooks (redacting secrets) + request/response events
- [ ] Rich rate-limit handling (respect bucket headers)
- [ ] Pluggable serialization; optional `pydantic` extra for validation
- [ ] Retries for connection errors (not just status codes)

### M4 — Developer experience
- [ ] Expand `docs/` with per-resource reference and recipes
- [ ] Publish API reference (mkdocstrings) to GitHub Pages
- [ ] More runnable examples; a short "cookbook"
- [ ] `py.typed` verified against downstream type-checking

### M5 — Release & distribution
- [ ] Finalize semantic-versioning policy and deprecation strategy
- [ ] PyPI trusted publishing via the release workflow (tag `v*`)
- [ ] Changelog automation
- [ ] 1.0.0 stability commitment

## Open questions

- What is the authoritative list of Naibu API resources and their schemas?
- Pagination style: cursor, offset, or page-number? (Currently cursor-based.)
- Does the API issue idempotency keys / support conditional requests?
- Are there webhooks requiring signature verification?
- Preferred base URL(s) and environment story (prod/sandbox)?

## How to extend

Follow the "Adding a resource" recipe in [AGENTS.md](AGENTS.md). Keep sync and
async variants in lockstep, add tests, and update this plan.
