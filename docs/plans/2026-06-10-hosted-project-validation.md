# Hosted Project Validation

status: completed

## Context

The repository has a strong static LocalAuthentication baseline and a legacy
Xcode build helper, but it has no current hosted validation. On systems with
Xcode, `scripts/check-baseline.py` also stops after static checks instead of
proving that `touchid.xcodeproj` remains parseable.

## Priorities

1. Add a pinned, read-only, bounded macOS workflow for the canonical `make check`
   gate.
2. Make the baseline parse `touchid.xcodeproj` whenever Xcode is available.
3. Preserve the non-macOS static path and keep live biometric prompts, signing,
   credentials, simulator authentication, and user biometric state outside CI.
4. Document the hosted validation boundary and enforce the workflow contract in
   the baseline itself.

## Implementation Units

### Workflow And Contract

Files:

- `.github/workflows/check.yml`
- `scripts/check-baseline.py`

Add push, pull-request, and manual triggers; read-only repository permissions;
concurrency cancellation; a bounded `macos-15` job; a commit-pinned checkout;
and the canonical `make check` command. Extend the checker to require those
properties and to run `xcodebuild -list -project touchid.xcodeproj` when Xcode
is installed.

### Documentation

Files:

- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`
- `docs/plans/2026-06-10-hosted-project-validation.md`

Describe project parsing as structural validation only. Do not imply that CI
performs biometric authentication or proves LocalAuthentication behavior on a
real enrolled device.

## Verification

- `python3 -m py_compile scripts/check-baseline.py`
- `sh -n build.sh`
- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted macOS `Check` workflow for the pushed commit

## Risks And Boundaries

- Current Xcode may parse this legacy project while being unable to compile its
  historical Swift source; the workflow must not claim full build support.
- Hosted checks must not invoke `evaluatePolicy`, request biometric enrollment,
  access authentication state, use signing material, or introduce secrets.
