# Authentication Failure Reason Tests Plan

status: completed

## Context

`ViewController.authenticationFailureReason` maps `LocalAuthentication` errors
to local in-memory status strings. That classification is deterministic and
should be covered by focused unit assertions instead of generated XCTest
placeholders.

## Objectives

- Keep authentication failure reason classification testable from XCTest.
- Enable app testability for the unit-test target.
- Replace generated XCTest placeholders with focused failure reason tests.
- Cover unavailable Touch ID and missing-error fallback behavior.
- Preserve local-only authentication state handling with no logging, networking,
  upload, tokens, or analytics.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `sh -n build.sh`
- `./build.sh`
- `git diff --check`
