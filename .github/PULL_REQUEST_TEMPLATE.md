---
name: Pull Request
description: Submit a change to AI-SKILL
title: "[<type>]: <description>"
labels: []
assignees: []
---

## What does this PR do?

A 1–3 sentence summary of the change and the motivation.

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing behaviour to change)
- [ ] Documentation update
- [ ] Refactor / cleanup
- [ ] CI / build / tooling
- [ ] Dependency upgrade

## Related issues

Fixes #<issue>, relates to #<issue>, …

## How has it been tested?

Describe the tests you ran and the results.

- [ ] Unit tests added / updated
- [ ] Integration tests added / updated
- [ ] Manually verified locally (`docker compose up`, `npm run dev`, …)
- [ ] Manually verified the production build (`docker build`)

## Screenshots / Recordings

If the change is visible, attach before/after screenshots or a short
screen-recording.

## Checklist

- [ ] I have read [`CONTRIBUTING.md`](../../blob/main/CONTRIBUTING.md)
- [ ] My code follows the project's style (`ruff format`, `prettier --write`)
- [ ] I have run the linters locally (`ruff check`, `mypy`, `eslint`, `tsc`)
- [ ] I have added / updated tests
- [ ] I have updated relevant documentation (README, docs/, docstrings)
- [ ] New and existing unit tests pass locally
- [ ] I have not introduced any new security warnings
- [ ] I have not committed any secrets, credentials, or `.env` files

## Breaking change notes

If the change is breaking, document the migration path for downstream
consumers (SDK users, API consumers, self-hosters).
