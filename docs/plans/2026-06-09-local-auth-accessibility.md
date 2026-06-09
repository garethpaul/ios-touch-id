# Local Auth Accessibility

status: completed

## Context

The sample exposes biometric authentication through an explicit button. The
button title is visible, but assistive technologies should also receive the
local-only privacy boundary and the disabled in-progress state.

## Completed Scope

- Added a ready accessibility label and hint for the local biometric action.
- Added an in-progress accessibility label and hint while authentication is
  running.
- Restored the ready accessibility copy after callback and preflight completion
  paths.
- Extended the static baseline and docs so accessibility text remains aligned
  with local-only authentication behavior.

## Verification

- `make check`
- `git diff --check`
