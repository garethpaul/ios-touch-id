# Explicit Local Authentication Plan

status: completed

## Context

`ios-touch-id` demonstrates `LocalAuthentication`. The existing baseline keeps authentication state local and avoids logging, but the sample still starts biometric authentication as soon as the view loads.

## Objectives

- Require an explicit user action before starting local biometric authentication.
- Disable the authentication action while a request is in progress.
- Preserve the local-only success/failure state handling and weak callback capture.
- Extend the static baseline so biometric prompts cannot move back into `viewDidLoad`.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `sh -n build.sh`
- `git diff --check`
