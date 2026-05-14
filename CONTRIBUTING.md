# Contributing Guide

## Branch Strategy

```
main          production-ready, protected
staging       pre-production integration
dev           active development base
feature/*     new features (branch from dev)
fix/*         bug fixes (branch from dev or main for hotfixes)
chore/*       tooling, deps, CI changes
```

## PR Checklist

Every pull request must satisfy all of the following before merge:

- [ ] Tests added or updated — coverage must not drop below 85%
- [ ] `make lint` passes with no errors
- [ ] `make typecheck` passes with no errors
- [ ] `make test` passes (all unit + relevant integration tests)
- [ ] `CHANGELOG.md` entry added under `[Unreleased]`
- [ ] Docstrings on all new public functions and classes
- [ ] No PHI in logs, no secrets in code, no hardcoded credentials
- [ ] `CLAUDE.md` updated if architecture or standards changed
- [ ] ADR created in `docs/decisions/` if a significant decision was made

## Commit Message Format

```
<type>(<scope>): <short summary>

[optional body — what and why, not how]

[optional footer — breaking changes, issue refs]
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`

Examples:
```
feat(ingestion): add Kafka consumer for patient.created topic
fix(api): return 422 when patient_id is not a valid UUID
chore(deps): pin pyspark to 3.5.1
```

## Changelog Format (Keep-a-Changelog)

```markdown
## [Unreleased]
### Added
- Short description of new feature

### Changed
- Description of change

### Fixed
- Bug description
```

## Security Rules

- Run `make check-env` before starting services
- Never bypass pre-commit hooks (`git commit --no-verify` is forbidden)
- Any suspected secret exposure: rotate immediately, then open a security issue
- PHI in test data: use Synthea-generated synthetic data only (see `tests/fixtures/`)
