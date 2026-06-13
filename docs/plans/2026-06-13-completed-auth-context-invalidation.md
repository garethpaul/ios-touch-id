# Completed Authentication Context Invalidation

status: completed

## Context

`viewDidDisappear` invalidates the active `LAContext`, but
`finishAuthentication` clears the retained context without invalidating it.
Normal callback completion and preflight failure therefore use a weaker teardown
path than view disappearance.

## Priority

LocalAuthentication contexts are security-sensitive, stateful objects. Every
accepted terminal path should explicitly invalidate the matching context before
releasing it, while stale callbacks must remain unable to affect a newer attempt.

## Requirements

- R1. Keep the attempt-identity guard as the first terminal-state predicate.
- R2. Invalidate the retained authentication context before clearing it.
- R3. Preserve attempt clearing, in-progress reset, button restoration, result
  assignment, and accessibility announcement ordering.
- R4. Preserve view-disappearance invalidation, explicit user initiation,
  fail-closed result classification, and local-only authentication behavior.
- R5. Add function-scoped static contracts and completed verification evidence.

## Implementation Units

### U1. Complete accepted-attempt teardown

- **File:** `touchid/ViewController.swift`
- Invalidate `authenticationContext` after accepting the attempt and before
  assigning nil.

### U2. Enforce terminal lifecycle ordering

- **File:** `scripts/check-baseline.py`
- Require the stale-attempt guard before invalidation, then context and attempt
  clearing before UI/result completion.

### U3. Document context ownership

- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- Record that accepted terminal paths invalidate retained biometric contexts.

## Scope Boundaries

- Do not change LocalAuthentication policy, fallback behavior, reason text,
  error classification, attempt identity, accessibility copy, or button layout.
- Do not add server identity, networking, persistence, analytics, logging, or
  credential storage.
- Do not claim live biometric validation without Xcode and supported hardware
  or simulator enrollment.

## Work Completed

- Invalidated the retained `LAContext` after accepting the current attempt and
  before clearing authentication state.
- Preserved stale-attempt rejection, view-disappearance invalidation, UI reset,
  result assignment, and accessibility announcement behavior.
- Added function-scoped teardown ordering contracts and documented terminal
  context ownership.

## Verification Completed

- All four Make gates, `make lint`, `make test`, `make build`, and `make check`,
  passed against the complete static baseline.
- `python3 -m py_compile scripts/check-baseline.py`, plist parsing, storyboard,
  XIB, workspace, and SVG XML parsing, app-icon JSON and workflow YAML parsing,
  `sh -n build.sh`, and `git diff --check` passed.
- Eight hostile mutations removing invalidation, moving it before attempt
  validation or after context clearing, removing or pre-clearing the attempt
  guard, announcing before state reset, or falsifying plan status or
  verification evidence were rejected.
- The local environment did not provide `xcodebuild` or enrolled biometrics, so
  live LocalAuthentication and simulator/device interaction were not claimed.
