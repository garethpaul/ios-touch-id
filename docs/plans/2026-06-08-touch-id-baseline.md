# iOS Touch ID Baseline Plan

status: completed

## Context

`ios-touch-id` is a legacy Swift sample for `LocalAuthentication` with a small
storyboard, app/test targets, and no external dependencies. This host does not
provide Xcode, so repository verification needs a static baseline while full
biometric validation remains a macOS/Xcode and compatible-device responsibility.

## Objectives

- Preserve the local biometric authentication sample flow.
- Remove authentication-state console logging.
- Use the callback authentication error when classifying biometric failures.
- Keep authentication status local in memory and avoid retaining the view
  controller from the authentication callback.
- Keep the prompt and documentation clear that local biometric success is not
  server identity proof.
- Add a portable build script that skips cleanly on hosts without Xcode.
- Add a reproducible `make check` target covering plist/storyboard/asset XML and
  JSON, Xcode project wiring, LocalAuthentication source, and local-only privacy
  guardrails.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `sh -n build.sh`
- `git diff --check`
