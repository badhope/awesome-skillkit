---
name: CLI Builder
name_zh:
description: 'The user wants a **real CLI** they can run by name'
description_zh:
category: terminal-cli
tags:
  - ai
  - api
  - backend
  - cli
  - database
source:
license: MIT
author: 'OpenAI (downstream pack: badhope)'
version: '0.1.0'
needs_review: false
slug: cli-builder
created: '2026-06-12'
updated: '2026-06-12'
inputs:
  - name: request
    type: string
    required: true
    description: User request or task description
output:
  format: markdown
  description: Generated content based on the user request
---
# When to use

The user wants a **real CLI** they can run by name
from any working directory — durable tool, not a
throwaway script. Typical triggers: "build me a CLI
for X", "wrap this API as a command-line tool", "I
keep running the same curl, turn it into a real
tool".

Use this when:

- The tool will be invoked more than once
- The same auth + retry + pagination shape will be
  re-used across jobs
- You want the output parseable (JSON) and the auth
  out of the shell history

**Do not** use this when a short script in the
current repo solves the task once and never again.
Write the script there.

# Inputs

- `tool_name` — the binary name to install
  (`ci-logs`, `slack-cli`, `sentry-cli`).
- `source_material` — what we're building against
  (OpenAPI spec, SDK, curl examples, internal
  script, web app, article).
- `first_jobs` — the literal first commands the
  CLI must support.
- `output_format` — JSON (default) / text / both.

# Output

A `## DESIGN` block followed by a `## SCAFFOLD`
block, then a `## INSTALL` block, then a `## USAGE`
block with one worked call. The agent should
actually create the project files in the chosen
location — this skill is build-it, not design-only.

# Prompt

```prompt
You are building a durable command-line tool.
The user will invoke it by name from any working
directory, possibly piped into `jq`, possibly
chained with other tools. Treat the CLI like a
public interface.

## 1. Name and scope

If the user gave a name, use it. If not, propose
a short, hyphen-free, lowercase name derived
from the tool's job (e.g. `ci-logs`,
`buildkite-logs`, `sentry-cli`).

Before scaffolding, check whether the proposed
command already exists:

  command -v <tool-name> || true

If it exists, choose a clearer install name or
ask the user.

## 2. Pick the runtime

Inspect what's on the machine first:

  command -v cargo rustc node pnpm npm python3 uv \
    || true

Then choose the least-surprising toolchain:

  - **Rust** — default for a durable CLI that will
    run from any repo. One fast binary, strong
    argument parsing, good JSON handling, easy
    copy into `~/.local/bin`.
  - **TypeScript / Node** — when the official SDK,
    auth helper, browser-automation library, or
    existing repo tooling is what makes the CLI
    better than a hand-rolled one.
  - **Python** — when the source is data science,
    local file transforms, notebooks, SQLite /
    CSV / JSON analysis, or Python-heavy admin
    tooling that still needs to install as a real
    command.

Do not pick a language that adds setup friction
unless it materially improves the CLI. If the best
language isn't installed, either install the
missing toolchain (with user approval) or choose
the next-best installed option.

State the choice in one sentence, including the
reason and the toolchain you found, before
scaffolding.

## 3. Sketch the command surface first

Before writing code, write the command surface in
chat:

  - binary name
  - `<tool> --help` shape
  - discovery commands: list resources, list
    projects, list regions
  - resolve / ID-lookup commands
  - read commands: get, show, list
  - write commands: create, update, delete,
    upload
  - raw escape hatch: `<tool> curl <path>` or
    `<tool> raw --method POST --body -` for cases
    the typed commands don't cover
  - auth / config choice: env var, keyring,
    `~/.config/<tool>/config.toml`
  - install command: `cargo install`,
    `npm install -g`, `uv tool install`,
    `pipx install`, or a `cp` into `~/.local/bin`

## 4. Defaults that matter

These are non-negotiable for a durable CLI:

  - **Default output is JSON** when `--format` is
    not passed. Stable schema across invocations.
  - **Text output is a `--format text` flag**, not
    a separate binary.
  - **Errors go to stderr** with a non-zero exit
    code. The JSON error shape is
    `{"error": {"code": "...", "message": "..."}}`.
  - **Pagination is a cursor** the caller can pass
    back via `--cursor`. Don't hide it.
  - **Auth is read from env first, config file
    second, never the command line** — keys must
    not appear in `ps` output.
  - **Dry-run is a global flag** (`--dry-run`)
    that prints the request it would have made
    and exits 0.
  - **Version is `tool --version`**, not buried in
    `help`.

## 5. Source-material-specific notes

  - **OpenAPI spec** — generate types from the
    spec, hand-write the wrapper. Don't commit
    the generated code if you can help it;
    re-generate.
  - **SDK docs** — wrap the SDK, don't reimplement
    the API. The CLI is a thin shell.
  - **Curl examples** — extract auth + base URL
    + request shape; do not literally encode
    example payloads.
  - **Internal script** — read it first, decide
    whether to refactor in place or re-implement.
    If the script is short, refactor in place.

## 6. Install

  - Rust: `cargo install --path .` or
    `cargo install --git <url>`
  - Node: `npm install -g .` (or `pnpm`, etc.)
  - Python: `uv tool install .` or `pipx install .`
  - Anywhere: `cp target/release/<tool>
    ~/.local/bin/` after a documented build

Document the install command in the README and
print it at the end of the scaffold step.

## 7. Pair with a wrapper skill

If the CLI is going to be used by an agent,
suggest pairing it with a thin skill that
documents the most common invocations and the
JSON shape. A good wrapper skill is 30-60 lines
and lives in `skills/<tool-cli>/SKILL.md`.
```

# When NOT to use

- **One-off script** — if this is a single
  invocation in the current repo, write a script
  in the repo. The CLI is overkill.
- **No durable commands in mind** — if the user
  only wants a "Hello, world" binary, this skill
  is too much ceremony.
- **Vendor SDK is already a CLI** — many APIs
  already ship an official CLI (e.g. `gh`,
  `aws`, `gcloud`). Wrap that, don't re-implement.
- **Browser automation task** — a CLI is the wrong
  shape; use a Playwright / browser-automation
  skill instead.
- **Sensitive auth on the command line** — the
  auth-must-not-be-in-`ps` rule will break naive
  invocations. Either use env vars + a config
  file, or pick a different shape.

# Example

**Input:**

```yaml
tool_name: "ci-logs"
source_material: "openapi-spec"
first_jobs:
  - "list recent failed jobs"
  - "download logs for a job"
  - "rerun a job"
output_format: "json"
```

**Output (the agent actually creates the files):**

```markdown
## DESIGN
Runtime: **Rust** (one fast binary, easy
`~/.local/bin` install, clap for argument
parsing, serde for JSON).

Command surface:
  ci-logs --help
  ci-logs auth login              # OAuth + token
                                  # storage in
                                  # ~/.config/ci-logs/auth.json
  ci-logs jobs list --limit 20 --since 24h
  ci-logs jobs get <id>
  ci-logs logs <job-id> --output <path>
  ci-logs jobs rerun <id>
  ci-logs raw --method GET --path /v1/jobs

Defaults: JSON to stdout, errors to stderr,
cursor pagination, --dry-run, --format text.

## SCAFFOLD
  ci-logs/
  ├── Cargo.toml
  ├── src/
  │   ├── main.rs          # clap subcommands
  │   ├── api.rs           # reqwest client
  │   ├── auth.rs          # token storage
  │   ├── jobs.rs          # list/get/rerun
  │   ├── logs.rs          # download
  │   └── output.rs        # JSON/text formatting
  ├── README.md            # install + auth flow
  └── skills/ci-logs/SKILL.md   # thin wrapper
                                 # skill for agent use

## INSTALL
  cargo install --path .
  # or, from a git checkout:
  cargo install --git https://example.com/ci-logs

## USAGE
  $ ci-logs jobs list --limit 5 --format text
  ID        STATE    STARTED              DURATION
  88412     failed   2026-06-10T14:22Z    4m12s
  88410     passed   2026-06-10T14:18Z    2m04s
  ...
```
