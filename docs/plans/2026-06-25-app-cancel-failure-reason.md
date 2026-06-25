# App Cancellation Failure Reason

status: completed

## Context

Apple documents `LAError.Code.appCancel` as the result produced when the app
cancels authentication. The sample recognized user and system cancellation but
let this known framework code fall through to the generic unknown-error copy.

## Design

Add an explicit `.appCancel` switch branch returning `app canceled
authentication`. Preserve the LocalAuthentication error-domain guard and the
generic fallback for missing, unrelated, or unrecognized errors.

## Test First

`testAuthenticationFailureReasonHandlesAppCancel` and its static source contract
were added before implementation. The baseline failed because the switch lacked
the required case.

## Verification

- `python3 scripts/check-baseline.py`
- `/usr/bin/make check`
- One hostile mutation removing the `.appCancel` branch
- `git diff --check`
- Local `xcodebuild` is unavailable; hosted macOS CI executes focused XCTest.

## Scope Boundaries

- Authentication policy, prompts, fallback visibility, context ownership,
  success validation, accessibility, privacy, bundle metadata, and deployment
  target are unchanged.
- Newer accessory-biometry codes are outside this iOS 12 sample's compile-time
  surface and continue through the generic fallback when unrecognized.

## Reference

- https://developer.apple.com/documentation/localauthentication/laerror-swift.struct/appcancel
