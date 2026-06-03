# ADR 009 — OWASP security headers middleware

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

Out of the box, FastAPI does not set HTTP security headers. The
OWASP Secure Headers project recommends a baseline that includes
HSTS, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
`Permissions-Policy`, a strict `Content-Security-Policy`, and the
`Cross-Origin-*` isolation headers.

## Decision

Add a single `SecurityHeadersMiddleware` that attaches the OWASP
baseline to every response, strips `X-Powered-By`, and normalises
the `Server` header. HSTS is added only when `DEBUG=false`.

## Consequences

- One file, ~50 lines, zero runtime overhead.
- The middleware sits between the error handler and the rate
  limiter so the headers are present even on error responses.
- Future additions (e.g. CSP nonces for a future server-rendered UI)
  have a clear home.
