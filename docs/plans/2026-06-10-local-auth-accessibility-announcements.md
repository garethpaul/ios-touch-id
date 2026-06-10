# Local Authentication Accessibility Announcements

status: completed

## Context

The sample updates the authentication button title, enabled state, accessibility
label, and accessibility hint as local biometric authentication starts and
finishes. VoiceOver users still need an explicit announcement for in-progress,
success, and failure state changes because those updates can occur without
focus moving.

## Completed Scope

- Added a local `announceAuthenticationStatus` helper using
  `UIAccessibilityAnnouncementNotification`.
- Announced the local in-progress authentication state when the request starts.
- Announced local success, callback failure, and unavailable-preflight results.
- Extended the static baseline and docs so accessibility announcements stay
  local-only and do not imply remote credential transfer.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
