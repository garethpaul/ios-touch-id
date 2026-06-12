# iOS Touch ID CI Baseline

status: completed

## Context

The Touch ID sample has a Python `make check` baseline for LocalAuthentication
behavior, metadata, docs, and local-only privacy guardrails. Full interaction
verification still requires compatible hardware or simulators. The missing
guard was a reproducible Python toolchain inside hosted Xcode validation.

## Changes

- Added `.github/workflows/check.yml` for GitHub Actions.
- Pinned Python 3.12 on macOS before running the static baseline.
- Combined the static baseline with the unsigned `build.sh` Xcode compilation.
- Extended the checker and docs so hosted CI stays visible.

## Verification

- `make check`
- `git diff --check`
