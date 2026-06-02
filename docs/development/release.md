# Release process

AI-SKILL follows [Semantic Versioning](https://semver.org/).
Releases are cut by a maintainer from the `main` branch.

## When to cut a release

- **Major** — breaking change to the REST API, the SDK public
  surface, or the data model that would force a self-hoster to run
  a migration
- **Minor** — new feature, new endpoint, new SDK method
- **Patch** — bug fix, dependency upgrade, doc fix

When in doubt, ship a minor.

## Pre-release checklist

1. **All CI green** on `main`
2. **CHANGELOG.md** is updated — the unreleased section is moved
   under a dated heading
3. **OpenAPI schema** is regenerated and committed (the
   `scripts/generate_openapi.py` script handles this in CI on
   `main`)
4. **Translations** are in sync (`make i18n-check`)
5. **No security advisories** open against the codebase
6. **Docker images** built and pushed (CI does this on tag)

## Cutting the release

```bash
# 1. Make sure you are on main, up to date, with a clean tree
git checkout main
git pull --ff-only
git status   # should be "nothing to commit, working tree clean"

# 2. Bump the version in all the relevant files
#    (use the `make bump-version` helper, or edit by hand)
make bump-version VERSION=1.2.0

# 3. Update CHANGELOG.md
$EDITOR CHANGELOG.md
#    Move the items from "Unreleased" to a new section with today's
#    date. Add the version comparison link at the bottom.

# 4. Commit and tag
git add -A
git commit -m "chore(release): bump to 1.2.0"
git tag -s -a 1.2.0 -m "Release 1.2.0"
git push origin main
git push origin 1.2.0
```

## CI on tag push

Pushing the tag triggers `deploy.yml`, which:

1. Runs the full test suite
2. Builds the Docker images (backend, frontend)
3. Pushes them to GitHub Container Registry with tags:
   - `latest`
   - the tag name
   - the short SHA
4. Creates a **draft** GitHub Release from the tag
5. Uploads the wheel + sdist for the Python SDK to the package
   registry (when configured)

A maintainer then:

1. Reviews the draft Release notes
2. Edits if needed
3. Publishes the Release

## Hotfixes

For a critical bug in production:

```bash
# 1. Branch from the release tag
git checkout -b hotfix/critical-bug 1.2.0

# 2. Fix and commit
$EDITOR …
git commit -m "fix(backend): address the critical bug"

# 3. Bump the patch version
make bump-version VERSION=1.2.1

# 4. Tag and push
git tag -s -a 1.2.1 -m "Hotfix 1.2.1"
git push origin hotfix/critical-bug
git push origin 1.2.1

# 5. Merge back to main
git checkout main
git merge --no-ff hotfix/critical-bug
git push origin main
```

## Pre-releases

For a Release Candidate or beta:

```bash
git tag -s -a 1.3.0-rc.1 -m "Release candidate"
git push origin 1.3.0-rc.1
```

The CI workflow tags the image with both `1.3.0-rc.1` and `next` so
beta testers can pull from the same tag.

## Deprecations

- A feature marked deprecated in a minor release must continue to
  work for at least one more minor release.
- The deprecation warning includes a `Sunset` header with the
  removal date.
- Removal is part of a major release.

## Where to go from here

- [Roadmap](../community/roadmap.md) — what is planned
- [Changelog](../community/changelog.md) — what has shipped
- [Deployment](../deployment.md) — promoting a build to production
