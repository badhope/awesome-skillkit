# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- i18n: gettext pipeline for backend strings (35 keys, `en` + `zh`).
  Run `make i18n-compile && make i18n-check` after editing `.po` files.
- i18n: `LocaleMiddleware` resolves locale from `?lang=` / `X-Locale` /
  `Accept-Language`, sets `request.state.locale`, and stamps `Content-Language`
  + `Vary` on the response.
- i18n: `localized_http_exception(request, status, message)` helper;
  auth + deps use it everywhere now.
- i18n: rate-limit 429 responses are translated; `Content-Language` and
  `Retry-After` both set.
- i18n: `Skill.content` JSONB may now follow the
  `{"default_locale": "en", "translations": {...}}` shape. `pick_translation`
  handles the fallback chain. `GET /skills?locale=zh` (list/detail) slices
  the response; `?locale=all` returns the full map.
- docs: enabled `mkdocs-static-i18n` with `docs_structure: folder`. English
  sources live in `docs/en/`, Chinese in `docs/zh/` (24/27 pages translated).
  `scripts/sync-docs.sh` updated to write into `docs/en/`.
- CI: `.github/workflows/i18n.yml` runs catalog check + mkdocs build for both
  locales, asserts that `site/zh/index.html` doesn't contain English copy.
- root: `README.zh.md`, `FAQ.zh.md`, `ROADMAP.zh.md`, `TROUBLESHOOTING.zh.md`,
  `CODE_OF_CONDUCT.zh.md`, `SECURITY.zh.md` translated.

### Changed

- `_(message, locale, **params)` is the new backend translation helper
  (replaces the 2-arg form). Used everywhere.
- Frontend `t(key, params)` supports `string.format`-style placeholders.
- `formatDate(..., "relative", locale)` and `formatNumber(value, locale)` use
  `Intl.RelativeTimeFormat` / `Intl.NumberFormat`.

### Fixed

- Frontend `Skills` / `Compositions` / `Dashboard` no longer hardcode English
  copy (charts, command menu, dialog, load-more, detail page).
- `i18n` consumer type errors now caught at build time.

### Notes

- Coverage status lives at `docs/zh/translation-coverage.md`; CI greps the
  pages listed as "translated" to make sure they still build.
- Legacy `Skill.content` flat-dict shape is still accepted — i18n shape is
  opt-in, so no breaking change for existing API consumers.

---

## [1.0.0] - 2026-06-01

First release. Ships an empty library — the platform is up, the dataset
intentionally isn't. Each operator seeds their own skills.

Backend: FastAPI, asyncpg, Alembic, Redis, Qdrant, Celery, Sentry, OTel.
Frontend: Next.js 15 App Router, PWA, mobile-first.
SDKs: Python (async) and TypeScript.
Auth: JWT with access/refresh rotation, RBAC.
Search: hybrid BM25 + dense, RRF fusion, sentence-transformers embeddings.
CI: GitHub Actions for lint/test/build/publish; Dependabot; pre-commit.
Docs: this mkdocs-material site.

---

[1.0.0]: https://github.com/badhope/AI-SKILL/releases/tag/v1.0.0
