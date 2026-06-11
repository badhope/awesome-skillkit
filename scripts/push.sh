#!/usr/bin/env bash
# scripts/push.sh - multi-method push to GitHub
#
# Usage:
#   ./scripts/push.sh                  # auto-pick best available auth
#   GH_TOKEN=ghp_xxx ./scripts/push.sh # HTTPS with token (askpass)
#   GIT_SSH_KEY=~/.ssh/id_ed25519 ./scripts/push.sh  # SSH with explicit key
#   FORCE=0 ./scripts/push.sh          # refuse-push if remote is ahead
#   PUSH_TAGS=0 ./scripts/push.sh      # skip tag push
#   CLEAN_OLD_TAGS=0 ./scripts/push.sh # skip remote tag cleanup
#
# Why this script exists: the sandbox has no creds by default.
# The user runs it with creds in env, or the user pre-configures
# ssh-agent / credential.helper.

set -euo pipefail

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
FORCE="${FORCE:-1}"              # default 1: force-push to overwrite old main
PUSH_TAGS="${PUSH_TAGS:-1}"
CLEAN_OLD_TAGS="${CLEAN_OLD_TAGS:-1}"

# Old-era tags to delete from remote (curated-link-list era, no longer relevant)
OLD_TAGS=(v0.0.1 v0.0.2 v0.1.0 v0.2.0)

log()  { printf '\033[1;36m[push]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m[fail]\033[0m %s\n' "$*"; exit 1; }
ok()   { printf '\033[1;32m[ok]\033[0m   %s\n' "$*"; }

cd "$(git rev-parse --show-toplevel)"

# 1. working tree must be clean
if ! git diff --quiet || ! git diff --cached --quiet; then
  fail "working tree not clean - commit first"
fi

HEAD="$(git rev-parse HEAD)"
log "local HEAD:  $HEAD"
log "local tag:   $(git tag -l | tr '\n' ' ')"
log "remote:      $(git remote get-url "$REMOTE")"

# 2. decide auth method, build PUSH_ENV
PUSH_ENV=()

if [[ -n "${GH_TOKEN:-}" ]]; then
  log "auth: GH_TOKEN via askpass"
  ASKPASS="$(mktemp)"
  printf '#!/bin/sh\nprintf "%%s" "%s"\n' "$GH_TOKEN" > "$ASKPASS"
  chmod +x "$ASKPASS"
  PUSH_ENV+=(GIT_ASKPASS="$ASKPASS")
  trap 'rm -f "$ASKPASS"' EXIT
elif [[ -n "${GIT_SSH_KEY:-}" ]] && [[ -f "${GIT_SSH_KEY}" ]]; then
  log "auth: SSH key at $GIT_SSH_KEY"
elif ssh-add -l &>/dev/null; then
  log "auth: SSH agent"
elif git config --get credential.helper >/dev/null; then
  log "auth: git credential.helper"
elif [[ -f "$HOME/.netrc" ]] || [[ -f "$HOME/.git-credentials" ]]; then
  log "auth: ~/.netrc or ~/.git-credentials"
else
  warn "no creds detected - set GH_TOKEN or pre-configure ssh/credential.helper"
fi

# 3. force-push main
PUSH_FLAG=()
if [[ "$FORCE" == "1" ]]; then
  PUSH_FLAG+=(--force-with-lease)
fi

log "push $BRANCH -> $REMOTE (force=$FORCE)"
env "${PUSH_ENV[@]}" git push "${PUSH_FLAG[@]}" "$REMOTE" "$BRANCH" || fail "git push failed"
ok "main pushed: $HEAD"

# 4. delete old remote tags
if [[ "$CLEAN_OLD_TAGS" == "1" ]]; then
  for t in "${OLD_TAGS[@]}"; do
    if env "${PUSH_ENV[@]}" git ls-remote --tags "$REMOTE" 2>/dev/null | grep -q "refs/tags/$t$"; then
      log "delete remote old tag: $t"
      env "${PUSH_ENV[@]}" git push "$REMOTE" ":refs/tags/$t" 2>&1 || warn "  delete $t failed (may not exist)"
    fi
  done
fi

# 5. push local tags
if [[ "$PUSH_TAGS" == "1" ]]; then
  log "push local tags to remote"
  env "${PUSH_ENV[@]}" git push --tags "$REMOTE" || fail "git push --tags failed"
  ok "tags pushed"
fi

# 6. verify
log "remote main tip:"
env "${PUSH_ENV[@]}" git ls-remote "$REMOTE" "$BRANCH" 2>/dev/null
log "remote tags:"
env "${PUSH_ENV[@]}" git ls-remote --tags "$REMOTE" 2>/dev/null | grep -v '\^{}' | head -20

ok "all done"
