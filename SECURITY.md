# Security Policy

## Supported versions

The latest released minor version receives security fixes.

## Reporting a vulnerability

Please **do not** open public GitHub issues for security vulnerabilities.

Instead, report them privately to **security@tamarisklabs.com**. Include:

- A description of the vulnerability and its impact.
- Steps to reproduce or a proof of concept.
- Affected version(s).

We aim to acknowledge reports within 3 business days and to provide a
remediation timeline after triage.

## Handling credentials

- Never commit API keys, client secrets, or `.env` files. The repository's
  `.gitignore` excludes `.env` by default.
- Prefer environment variables (`NAIBU_API_KEY`, `NAIBU_CLIENT_ID`, ...) over
  hard-coded credentials.
