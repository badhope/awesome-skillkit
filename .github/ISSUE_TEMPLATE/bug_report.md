---
name: Bug Report
description: Report a defect or unexpected behaviour
title: "[Bug]: "
labels: ["bug", "needs-triage"]
assignees: []
---

## Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. …
2. …
3. …

```bash
# Commands you ran (or API requests you made)
curl ...
```

## Expected Behaviour

What you expected to happen.

## Actual Behaviour

What actually happened. Include the full error message / stack trace.

```text
ERROR:  ...
Traceback (most recent call last):
  File "..."
  ...
```

## Environment

| Item | Value |
|------|-------|
| AI-SKILL release | `latest` (or commit SHA) |
| Deployment | docker-compose / manual / k8s |
| OS | `Ubuntu 22.04`, `macOS 15`, … |
| Backend | `python 3.12.4`, image tag, … |
| Frontend | `node 20.x`, image tag, … |
| Database | `postgres 16.2`, `redis 7.4`, `qdrant 1.9.x` |

## Logs

If available, attach backend logs (`docker compose logs backend` or
`kubectl logs …`) and frontend browser dev-tools network output.

## Severity

How is this affecting you? (choose one)

- [ ] Blocker — production is down
- [ ] High — major feature unusable
- [ ] Medium — workaround exists
- [ ] Low — cosmetic / minor

## Additional Context

Anything else that might help — screenshots, linked PRs, related issues.

## Checklist

- [ ] I have searched the [existing issues](../../issues) and confirmed this is not a duplicate
- [ ] I have read [`CONTRIBUTING.md`](../../blob/main/CONTRIBUTING.md)
- [ ] I am willing to submit a PR fixing the bug (optional)
