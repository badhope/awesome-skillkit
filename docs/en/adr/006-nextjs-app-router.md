# ADR 006 — Next.js 15 App Router

- **Status**: Accepted
- **Date**: 2026-06-01

## Context

The frontend is a public-facing skill browser. It needs SEO,
streaming, server components, and a strong story for internationalization.

## Decision

Use **Next.js 15 with the App Router** and React 19.

## Rationale

- Server Components give us a free pass on the "loader / suspense"
  dance.
- The App Router's file-based routing is easy to navigate.
- Built-in i18n story, though we rolled our own for finer control.
- Edge / static rendering options out of the box.

## Alternatives considered

| Option         | Why not                                       |
|----------------|-----------------------------------------------|
| Pages Router   | Legacy; no RSC; the community is on App Router |
| Remix          | Excellent but smaller ecosystem of UI libs    |
| Astro          | Great for content sites; weaker for an app     |
| Plain React + Vite | Lacks SEO and SSR without extra work       |

## Consequences

- We must use `'use client'` sparingly; most pages are RSC.
- Streaming is enabled by default; we lean on `<Suspense>` for
  search results.
- We avoid `'use client'`-only libraries (e.g. those that touch
  `window` at import time).
