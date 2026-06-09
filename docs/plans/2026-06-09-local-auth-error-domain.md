# Local Auth Error Domain Guard

status: completed

## Context

`authenticationFailureReason` classified failures by numeric error code. Numeric
codes can collide across unrelated `NSError` domains, so the sample should only
map LocalAuthentication-specific messages when the error comes from
`LAErrorDomain`.

## Objectives

- Require `LAErrorDomain` before mapping LocalAuthentication error codes.
- Keep missing or unrelated errors on the generic local failure message.
- Add XCTest coverage for unrelated error domains.
- Extend the static baseline and docs to capture the error domain guard.

## Verification

- `make check`
- `git diff --check`
