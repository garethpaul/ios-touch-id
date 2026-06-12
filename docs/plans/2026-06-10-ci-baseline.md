# iOS Touch ID CI Baseline

status: completed

## Context

The Touch ID sample has an SDK-free `make check` baseline for
LocalAuthentication behavior, metadata, docs, and local-only privacy guardrails.
Full app verification still requires macOS, Xcode, and compatible hardware or
simulators. The missing guard was hosted CI for the static baseline.

## Changes

- Added `.github/workflows/check.yml` for GitHub Actions.
- Ran the Python static baseline on Ubuntu with Python 3.12.
- Kept full `build.sh`/Xcode verification documented as a macOS toolchain task.
- Extended the checker and docs so hosted CI stays visible.

## Verification

- `make check`
- `git diff --check`
