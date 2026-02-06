# AGENTS.md

This file defines repository-specific working conventions to keep implementation, documentation, and release workflows consistent.

## Scope

- Repository: actively maintained fork of `whs/django-static-compress`.
- Main integration branch: `dev`.
- Goal: preserve behavior, improve quality incrementally, and keep release history clean.

## Working Language

- Write documentation and process notes in English.
- Keep commit messages in English.

## Branching Model

- Use short-lived topic branches from `dev`.
- Preferred branch prefixes:
  - `fix/...`
  - `perf/...`
  - `refactor/...`
  - `clarify/...`
  - `test/...`
  - `docs/...`
  - `ci/...`
  - `chore/...`
- Merge topic branches into `dev` after validation.

## Step-by-Step Planning (Required)

For non-trivial work, always provide a step-by-step plan before implementation.

- Plans must be explicit and executable.
- Number each section from `1` (per section), not globally.
- Before executing a step, restate the step textually when requested.
- Execute one step at a time and report completion before moving on.

## Commit Discipline (Required)

- Prefer small, focused commits with one clear intent.
- Avoid bundling unrelated changes in a single commit.
- Separate commits by concern, for example:
  - behavior change
  - tests
  - docs/changelog
  - CI/tooling
- Commit message style:
  - imperative mood
  - concise
  - no trailing period
  - aligned with existing repo history style

## Changelog Rules

- Format: Keep a Changelog style.
- Include only necessary and meaningful entries.
- Group related changes into one entry when they describe one user-visible outcome.
- Avoid over-documenting internal micro-commits.
- Use `Tests:` prefix for test-coverage entries when relevant.
- Do not place post-release changes into already released sections.
- Any new work after a tag must stay under `Unreleased`.

## Versioning and Release

- Use SemVer:
  - `MAJOR` for breaking compatibility changes.
  - `MINOR` for backward-compatible features.
  - `PATCH` for fixes, maintenance, docs/tooling-only releases.
- During release cut:
  - move `Unreleased` entries into the new version section with date.
  - update changelog compare links.
- Tags:
  - annotated tags only, format `vX.Y.Z`.
  - push tag to `origin` and verify remote presence.

## Validation Checklist Before Merge/Release

Run all of the following:

1. `python -m pre_commit run --all-files`
2. `python -m unittest discover -s test`
3. `cd integration_test; python manage.py test`

## Local vs CI Lint/Format Policy

- Local: autofix is allowed for developer productivity.
- CI: check-only mode (no autofix in workflow).
- CI Ruff commands:
  - `python -m ruff check --no-fix .`
  - `python -m ruff format --check .`

## Tooling Baseline

- `requirements-dev.txt` includes development tools only.
- `pyproject.toml` is the source of truth for Ruff/build settings.
- Keep pre-commit hooks modern and maintained; avoid legacy/archived integrations.

## Package Metadata Policy

- Preserve original author attribution.
- Keep fork maintainer metadata up to date.
- Repository URL should point to the active fork.

## Documentation Policy

- README must reflect active maintenance status.
- Remove obsolete badges/instructions when they no longer match reality.
- Keep development commands current (no legacy `setup.py develop/test` guidance).

