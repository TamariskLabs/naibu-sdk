# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-09

### Added

- Initial release of the Naibu Python SDK.
- Synchronous `NaibuClient` and asynchronous `AsyncNaibuClient`.
- Authentication providers: `ApiKeyAuth` and `OAuth2ClientCredentials`
  (with automatic token caching/refresh).
- Automatic retries with exponential backoff + jitter for transient failures.
- Typed exception hierarchy mapped from HTTP status codes.
- Auto-paginating list helpers (`SyncPage` / `AsyncPage`).
- Example resources: customers, products, orders, invoices.
- Full typing support (`py.typed`).

[Unreleased]: https://github.com/TamariskLabs/naibu-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/TamariskLabs/naibu-sdk/releases/tag/v0.1.0
