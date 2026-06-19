# Biometric-Neutral Failure Copy

status: completed

## Context

The app now declares a Face ID purpose and uses the generic biometric policy,
but `authenticationFailureReason` still reports “touch id unavailable,” “touch
id not enrolled,” and “touch id locked” for every device. Those announcements
are inaccurate on Face ID hardware and expose legacy implementation wording
through both visible and accessibility status updates.

## Priority

Align failure copy with the policy the app actually evaluates. Biometric-neutral
messages remain truthful across Touch ID and Face ID without adding device
probing, changing authentication policy, or expanding the privacy surface.

## Requirements

- R1. `biometryNotAvailable` must report that biometric authentication is
  unavailable without naming a specific sensor.
- R2. `biometryNotEnrolled` must report that biometric authentication is not
  enrolled without naming a specific sensor.
- R3. `biometryLockout` must report that biometric authentication is locked
  without naming a specific sensor.
- R4. Missing errors, unrelated error domains, user fallback, failed results,
  contradictory results, and successful results must retain their behavior.
- R5. Authentication policy, localized reason, fallback title, attempt identity,
  context invalidation, UI state, and accessibility announcement flow must not
  change.
- R6. Hosted XCTest and portable static contracts must reject stale Touch ID
  copy, missing neutral messages, or incomplete plan and guidance evidence.

## Implementation Units

### U1. Neutralize biometric failure messages

**File:** `touchid/ViewController.swift`

Replace the three sensor-specific strings in the existing LocalAuthentication
error switch with concise biometric-neutral messages.

### U2. Regression coverage

**Files:** `touchidTests/touchidTests.swift`, `scripts/check-baseline.py`

Update focused XCTest expectations and require the neutral strings while
forbidding the stale Touch ID variants in executable source and tests.

### U3. Maintained evidence

**Files:** `AGENTS.md`, `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`,
and this plan.

Document biometric-neutral failure copy while preserving the local-only,
fail-closed authentication and Face ID purpose boundaries.

## Test Scenarios

- Unavailable biometrics return “biometric authentication unavailable.”
- Unenrolled biometrics return “biometric authentication not enrolled.”
- Biometric lockout returns “biometric authentication locked.”
- Missing or unrelated errors remain generic.
- User fallback remains explicit without claiming an implemented password flow.
- Successful, failed, and contradictory completion pairs remain fail closed.

## Scope Boundaries

- Do not change LocalAuthentication policy, context lifecycle, attempt identity,
  accessibility mechanics, button layout, plist purpose text, or storyboard.
- Do not add device-model checks, networking, persistence, analytics, logging,
  credential storage, or fallback authentication.
- Do not claim live biometric execution on Linux.

## Verification

- Run all four Make gates from the checkout and the absolute Makefile from an
  external directory.
- Compile the checker, validate `build.sh`, and run `git diff --check`.
- Reject isolated mutations for unavailable, unenrolled, and lockout copy,
  stale Touch ID wording, XCTest coverage, guidance, and completed plan
  evidence.
- Audit intended files for generated artifacts, protected metadata, and
  credential-shaped additions.

## Work Completed

- Replaced unavailable, unenrolled, and lockout messages with
  biometric-neutral LocalAuthentication copy.
- Added focused XCTest and portable source, test, guidance, and
  completed-evidence contracts without changing policy, context lifecycle, UI
  mechanics, plist, or project metadata.

## Verification Completed

- All four Make gates passed after the completed implementation.
- The absolute Makefile check passed from an external directory.
- `python3 -m py_compile scripts/check-baseline.py`, `sh -n build.sh`, and
  `git diff --check` passed.
- Seven isolated hostile mutations were rejected for the three neutral
  messages, stale sensor wording, XCTest discovery, guidance, and plan
  evidence.
- Generated-artifact, protected-metadata, conflict-marker, and changed-line
  credential audits passed.
- Local `xcodebuild was unavailable`; hosted macOS remains authoritative for
  Swift compilation and XCTest.
