# Local Auth In-Progress Title

status: completed

## Context

The authentication button had accessibility text for the in-progress state, but
its visible disabled title did not change while LocalAuthentication was running.
Sighted users should receive the same local in-progress signal.

## Completed Scope

- Added an `Authenticating...` disabled-state title before disabling the button.
- Kept the ready title restored through the shared ready-state helper.
- Preserved explicit, user-triggered LocalAuthentication behavior.
- Extended the static baseline and docs so the in-progress title remains aligned
  with the local-only authentication state.

## Verification

- `make check`
- `git diff --check`
