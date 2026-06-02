# AI-SKILL — Documentation

This folder holds long-form documentation that does not fit in the
top-level README.

## Start here

| Document | Purpose |
|---|---|
| [architecture.md](architecture.md) | Layered system architecture, request lifecycle, data model, search pipeline, deployment topology, security model, observability |
| [deployment.md](deployment.md) | Local Docker, manual install, single-VPS, managed cloud (Vercel / Fly.io / Render / AWS) |
| [development.md](development.md) | Project layout, conventions, how to add an endpoint / page / SDK method, database changes, testing, release process |
| [troubleshooting.md](troubleshooting.md) | Common errors and their fixes (boot, DB, frontend, search, performance, auth, CI) |

## Diagrams

| File | Source |
|---|---|
| [assets/architecture.svg](assets/architecture.svg) | Layered architecture overview (rendered in the README) |
| [assets/data-model.svg](assets/data-model.svg) | Entity-relationship diagram of the SQL schema |

The SVG files are hand-authored and committed (no external tooling
required to render them). If you change the architecture, please
update the SVGs in the same PR.

## See also

- Top-level [README](../README.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md) and [SECURITY.md](../SECURITY.md)
- [ROADMAP.md](../ROADMAP.md) and [FAQ.md](../FAQ.md)
- [examples/](../examples/) for runnable code samples
