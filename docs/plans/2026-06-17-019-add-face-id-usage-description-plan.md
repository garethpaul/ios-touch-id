---
title: Face ID Usage Description
type: fix
date: 2026-06-17
---

# Face ID Usage Description

## Summary

Add the required `NSFaceIDUsageDescription` privacy key for the app's biometric
authentication policy and lock the requirement into the canonical baseline.
Keep the value specific to the sample's local-only authentication behavior.

## Problem Frame

`ViewController` evaluates `.deviceOwnerAuthenticationWithBiometrics`, which
supports both Touch ID and Face ID, but the application plist does not contain
`NSFaceIDUsageDescription`. Apple requires that key for apps that use APIs that
access Face ID; without it, Face ID authorization requests may fail.

Primary references:

- <https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription>
- <https://developer.apple.com/documentation/localauthentication/lapolicy/deviceownerauthenticationwithbiometrics>
- <https://developer.apple.com/documentation/localauthentication/logging_a_user_into_your_app_with_face_id_or_touch_id/>

## Requirements

- R1. Add `NSFaceIDUsageDescription` to the application plist as a non-empty,
  user-facing string.
- R2. Explain that Face ID is used only for local authentication and do not
  imply credential collection, upload, account login, or server identity.
- R3. Preserve the explicit button-triggered biometric policy, fail-closed
  result handling, context invalidation, accessibility behavior, and iOS 12
  project settings.
- R4. Extend the canonical checker to parse the plist value and reject a
  missing, blank, generic, or network-oriented description.
- R5. Synchronize README, security, vision, and change documentation with the
  Face ID privacy contract.
- R6. Validate from the checkout and an external directory, reject isolated
  plist/checker/docs mutations, and require the existing hosted macOS XCTest
  job on the exact head.

## Key Technical Decisions

- **Use the standard plist key:** no runtime branching or Face ID detection is
  needed because the existing policy already delegates biometric selection to
  LocalAuthentication.
- **Describe actual data flow:** the message states that authentication remains
  on the device, matching the existing local-only sample and security posture.
- **Enforce semantics, not only presence:** the checker parses the plist and
  requires local authentication language so an empty or misleading value
  cannot satisfy the gate.

## Implementation Units

### U1. Declare Face ID purpose

- **Goal:** Make Face ID authorization eligible with an accurate privacy
  message.
- **Files:** `touchid/Info.plist`
- **Verification:** Parse the plist and assert the exact non-empty purpose
  string.
- **Covers:** R1, R2, R3.

### U2. Lock the privacy contract

- **Goal:** Prevent removal or weakening of the required purpose string.
- **Files:** `scripts/check-baseline.py`
- **Verification:** Baseline failures for a missing key, blank value, and a
  description that does not state local authentication.
- **Covers:** R4, R6.

### U3. Synchronize maintenance guidance

- **Goal:** Explain why the plist key is required and preserve the local-only
  boundary.
- **Files:** `README.md`, `SECURITY.md`, `VISION.md`, `CHANGES.md`
- **Verification:** Mutation-sensitive documentation tokens in the canonical
  checker.
- **Covers:** R5, R6.

## Risks And Mitigations

- A vague privacy string can pass a presence-only check; parse and validate the
  actual string value.
- A message that suggests remote identity verification would contradict the
  sample; require local and on-device language and reject network terminology.
- Linux cannot compile or present LocalAuthentication UI; retain local static
  gates and use the existing hosted macOS XCTest job as the compile boundary.

## Scope Boundaries

- Do not change the authentication policy, fallback behavior, error mapping,
  button flow, state machine, tests, deployment target, signing, or project
  structure.
- Do not add accounts, networking, analytics, credential storage, keychain
  persistence, or a custom Face ID prompt.
- Do not rename the historical project or rewrite Touch ID-specific result
  messages in this pass.

## Verification

- Run `make lint`, `make test`, `make build`, and `make check` from the checkout.
- Run all four Make gates through the absolute Makefile path from an external
  directory.
- Compile the Python checker, validate `build.sh`, parse `touchid/Info.plist`,
  and run `git diff --check`.
- Reject isolated mutations for a missing key, blank value, misleading privacy
  text, missing documentation, and weakened checker enforcement.
- Audit the exact diff, generated artifacts, and secret-like values.
- Require the exact-head hosted pull-request XCTest job before merge.

## Acceptance Criteria

- Face ID has a non-empty, accurate usage description in the application plist.
- The canonical checker rejects removal or semantic weakening of that value.
- Documentation states that biometric authentication remains local and
  on-device.
- All available local gates and mutations pass, and hosted XCTest evidence is
  recorded truthfully for the exact head.
