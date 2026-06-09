# Local Auth Unavailable Reasons Plan

status: completed

## Context

`ios-touch-id` keeps authentication state local and uses the callback error for biometric failures. Preflight failures for unavailable biometric hardware or unenrolled biometrics still collapse into the generic failure message.

## Objectives

- Classify unavailable biometric hardware locally.
- Classify unenrolled biometric state locally.
- Preserve explicit, user-triggered authentication and local-only state handling.
- Extend the static baseline so these failure reasons remain visible.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `sh -n build.sh`
- `./build.sh`
- `git diff --check`
