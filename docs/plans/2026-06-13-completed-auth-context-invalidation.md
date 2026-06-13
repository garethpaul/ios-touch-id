# Completed Authentication Context Invalidation

status: planned

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

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- Parse plist, storyboard, XIB, workspace, project, workflow, JSON, and SVG
  metadata with available local parsers.
- `sh -n build.sh`
- `git diff --check`
- Hostile mutations removing invalidation, moving it before attempt validation
  or after context clearing, weakening stale-attempt rejection, or falsifying
  plan evidence must be rejected.
