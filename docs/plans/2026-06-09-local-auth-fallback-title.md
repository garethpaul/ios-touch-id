# Local Auth Fallback Title

status: completed

## Context

The sample demonstrates local biometric authentication only. The default
LocalAuthentication fallback affordance can imply that the app has an alternate
password flow, but this sample does not implement one.

## Objectives

- Hide the LocalAuthentication fallback title during biometric evaluation.
- Keep `LAError.UserFallback` classified locally with generic fallback wording.
- Add focused failure reason coverage for the user-fallback error.
- Extend the static baseline so the fallback title guard remains visible without
  Xcode.
- Preserve local-only behavior without adding accounts, tokens, networking,
  uploads, or analytics.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
