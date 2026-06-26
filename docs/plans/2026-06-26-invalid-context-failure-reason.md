# Invalid Context Failure Reason

status: completed

## Problem

The sample invalidates `LAContext` instances after accepted completion paths and
when the view disappears, but Apple's known `LAError.Code.invalidContext` still
fell through to the generic unknown-error message.

## Design

Add an explicit `.invalidContext` switch branch returning `authentication
context invalid`. Preserve the LocalAuthentication error-domain guard, stale
attempt identifier check, fail-closed result normalization, and generic fallback
for missing, unrelated, or unrecognized errors.

## Test First

`testAuthenticationFailureReasonHandlesInvalidContext` and its static source
contract were added before implementation. The baseline failed because the
switch lacked the required case.

## Verification

- `python3 scripts/check-baseline.py`
- `/usr/bin/make lint`, `/usr/bin/make test`, `/usr/bin/make build`, and
  `/usr/bin/make check` from the checkout and through the absolute Makefile path
  from `/tmp`
- One hostile mutation removing the `.invalidContext` branch
- `python3 -m py_compile scripts/check-baseline.py`
- `sh -n build.sh`
- `git diff --check`
- Local `xcodebuild` is unavailable; hosted macOS CI executes focused XCTest.

## Scope Boundaries

- Authentication policy, prompts, fallback visibility, context ownership,
  success validation, accessibility, privacy, bundle metadata, deployment
  target, and stale completion handling are unchanged.
- Unknown codes and non-LocalAuthentication domains remain generic and fail closed.

## Reference

- https://developer.apple.com/documentation/localauthentication/laerror-swift.struct/code/invalidcontext
