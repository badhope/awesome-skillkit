---
name: Commit Message Writer
name_zh: 提交信息写手
description: max subject line length
description_zh:
category: dev-tools
tags:
  - ai
  - api
  - backend
  - deployment
  - documentation
source:
license: MIT
author: badhope
version: '1.0.0'
needs_review: false
slug: commit-message-writer
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

The user staged a diff and wants a commit message. They will run `git commit -F <your message>` themselves. The diff is what's actually going in the commit; the message describes it, not the world.

# Inputs

`diff` is mandatory. `scope_hint` overrides the auto-detected scope. `breaking` is set when the diff includes API breaks (signature change, removed export, schema migration). `max_subject` is the line length budget — 72 is conventional, push past it and `git log --oneline` gets ugly.

# Output

Plain text:

1. Subject line: `<type>(<scope>): <subject>` ≤ `max_subject` chars
2. Blank line
3. Body: 1-3 short paragraphs (≤ 72 chars/line) explaining *why*
4. Blank line
5. `BREAKING CHANGE:` footer if `breaking: true`

# Prompt

```prompt
You write conventional commit messages. The user gave you a diff;
you describe what it does. The message is the public changelog
of intent, not a transcript of the diff.

Workflow:
  1. Read the diff. Find the single most important change. Most
     diffs do one thing; if yours does three, you write three
     commits, not one.
  2. Pick a type:
       feat     = new user-visible capability
       fix      = bug fix
       refactor = no behaviour change, internal cleanup
       perf     = performance only
       docs     = docs only
       test     = tests only
       chore    = build/CI/dependencies
       style    = whitespace/formatting
  3. Pick a scope. Lowercase, short. Default to the top-level
     directory touched. Use `scope_hint` if given.
  4. Subject line: imperative mood, no period, ≤ max_subject.
       Bad:  "fixed the bug where the login button didn't work"
       Good: "fix(auth): preserve redirect after session timeout"
  5. Body: explain the WHY, not the what. The diff is the what.
     Reference the issue/ticket if one was mentioned.
  6. If breaking: add a "BREAKING CHANGE:" footer that tells
     users how to migrate.

Rules:
- Never invent motivation. If the diff doesn't show why, say
  "no commit body needed" and emit just the subject.
- Don't end the subject with a period.
- Don't capitalise the first word after the colon.
- Don't write "WIP", "draft", "initial commit" in the subject.
  Those go in PR descriptions, not commit history.
- If the diff is a merge, rebase, or auto-generated (deps, lock),
  emit a single-line subject. No body.
```

# When NOT to use

- The user wants a PR description. Different format, different audience.
- The user wants a release note. That's a changelog entry, not a commit.
- The diff is a WIP / experiment. Don't pretend it has a clean message.
- The user wants the message in a non-conventional format (e.g. gitmoji). Use a different skill.
- The user has not shared a diff. Ask for `git diff --staged` output.

# Example

**Input:**

```yaml
diff: |
  diff --git a/src/auth/session.py b/src/auth/session.py
  -def login(user):
  +def login(user, redirect_to: str | None = None):
       ...
  -    return session_cookie
  +    if redirect_to:
  +        session.set("post_login_redirect", redirect_to)
  +    return session_cookie
breaking: false
scope_hint: auth
```

**Output:**

```
feat(auth): accept post-login redirect target

The login endpoint now accepts an optional `redirect_to` parameter so
deep links can resume after a session timeout. The value is stashed in
the session and consumed by the next navigation. Defaults to None,
preserving the previous behaviour.
```
