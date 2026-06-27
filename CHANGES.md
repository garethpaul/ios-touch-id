# Changes

- Preserved space-containing absolute Makefile roots and rejected ambiguous
  loaded-file authority without changing authentication behavior.

## 2026-06-26 14:05 PDT - P2 - Classify unavailable authentication interaction

### Summary

Mapped LocalAuthentication's known `.notInteractive` result to explicit local
failure copy instead of treating it as an unknown authentication error.

### Work completed

- Added the missing noninteractive-result branch to failure classification.
- Added focused XCTest and static contracts for the known error code.
- Preserved the error-domain guard, stale-attempt rejection, fail-closed result
  normalization, and generic handling for unrelated domains and unknown codes.

### Threads

- Started: none — the bounded classification change was completed directly.
- Continued: none.
- Stopped: none.

### Files changed

- `touchid/ViewController.swift` — classifies `.notInteractive` explicitly.
- `touchidTests/touchidTests.swift` — covers the known framework result.
- `scripts/check-baseline.py` — binds the source, test, and completed plan.
- `README.md`, `SECURITY.md`, `VISION.md`, and the completed plan — record the
  local-only failure boundary.

### Validation

- Red-first source contract failed on the missing `.notInteractive` branch.
- Every Make alias passed from the checkout, and `make check` passed through the
  absolute Makefile path from `/tmp`.
- Four bundle-identifier mutations and the isolated hostile removal of the new
  branch were rejected.
- Python compilation, shell syntax, and `git diff --check` passed.
- Hosted macOS baseline, Swift build, and focused XCTest passed.
- CodeQL Actions, Python, and Swift analysis passed.
- Immutable manual review of exact head
  `799d3023bf13914668641b39a8611b7655bf1696` found no actionable issue.
- That reviewed head merged to master as
  `08fbd0ed113a832fc4d7e91eaef53b555a40f3ba`.

### Bugs / findings

- P2: Apple's known forbidden-authentication-UI code fell through to the same
  message as unknown codes and unrelated error domains.

### Review limitations

- `xcodebuild` is unavailable locally; hosted macOS CI remains authoritative for
  Swift, UIKit, LocalAuthentication, and XCTest execution.
- `$codex-review` was attempted against `origin/master`, but stopped before
  analysis with OpenAI HTTP 401 authentication failure. No review finding was
  suppressed; the exact diff received an immutable manual review.

### Next action

- Continue repository maintenance from the merged, fully green master head.

## 2026-06-26 - P2 - Classify invalid authentication contexts

### Summary
Mapped LocalAuthentication's known `.invalidContext` result to explicit local
failure copy instead of treating it as an unknown authentication error.

### Work completed
- Added the missing invalidated-context branch to failure classification.
- Added focused XCTest and static contracts for the known error code.
- Preserved stale-attempt rejection and generic handling for unrelated domains
  and unknown codes.

### Validation
- The source contract failed before implementation on the missing switch branch.
- Local and hosted verification evidence is recorded in the completed plan.

### Bugs / findings
- P2: Apple's known previously-invalidated context code fell through to the same
  message as unknown codes and unrelated error domains.

### Blockers
- `xcodebuild` is unavailable locally; hosted macOS CI remains authoritative for
  Swift, UIKit, LocalAuthentication, and XCTest execution.

### Next action
- Merge only after exact-head review and hosted checks pass.

## 2026-06-25 05:19 - P2 - Classify app-canceled authentication

### Summary
Mapped LocalAuthentication's known `.appCancel` result to explicit local
cancellation copy instead of treating it as an unknown authentication failure.

### Work completed
- Added the missing app-cancellation branch to failure classification.
- Added focused XCTest and static contracts for the known error code.

### Threads
- Started: none — work completed directly in the current repository.
- Continued: none.
- Stopped: none.

### Files changed
- `touchid/ViewController.swift` — classified `.appCancel` explicitly.
- `touchidTests/touchidTests.swift` — added the regression expectation.
- `scripts/check-baseline.py` — required source, test, and plan evidence.
- Documentation and plan files — recorded the fail-closed boundary.

### Validation
- `python3 scripts/check-baseline.py` — failed on the missing source branch
  before implementation and passed afterward.
- `/usr/bin/make check` — passed the static baseline, four bundle-identifier
  mutations, and conditional hosted-test gate; Xcode was unavailable locally.
- One isolated hostile mutation removing the `.appCancel` branch was rejected.
- Python compilation, shell syntax, and `git diff --check` — passed.
- Hosted Swift/XCTest and CodeQL checks — pending PR verification.

### Bugs / findings
- P2: Apple's known app-initiated cancellation code fell through to the same
  message as unknown codes and unrelated error domains.

### Blockers
- `xcodebuild` is unavailable locally; hosted macOS CI remains authoritative for
  Swift, UIKit, LocalAuthentication, and XCTest execution.

### Next action
- Open a PR and complete Codex plus hosted review before merge.

## 2026-06-21

- Aligned target-local app and XCTest bundle identifiers with their existing
  Info.plist identifiers and added four configuration-specific mutation checks.

## 2026-06-18

- Replaced Touch ID-specific unavailable, unenrolled, and lockout messages with
  biometric-neutral failure copy covered by focused XCTest.

## 2026-06-17

- Added the required Face ID usage description with a local and on-device
  authentication purpose.

## 2026-06-16

- Executed the focused LocalAuthentication message-mapping XCTest suite on an
  available hosted iPhone simulator instead of compiling the test target only.

## 2026-06-13

- Made all Make verification aliases location-independent when invoked through
  an absolute Makefile path.
- Added terminal context invalidation before accepted authentication attempts
  clear their retained `LAContext`.

## 2026-06-12

- Normalized LocalAuthentication callback results through a tested fail-closed
  path that requires a true success flag and no accompanying error.

## 2026-06-10

- Migrated the app and failure-reason tests to Swift 5 and iOS 12 with current
  UIKit and LocalAuthentication APIs.
- Invalidated active authentication contexts when the screen disappears and
  ignored stale completion callbacks by attempt identifier.
- Upgraded `make check` and hosted macOS validation to compile the unsigned app
  and XCTest target.
- Added a GitHub Actions workflow that runs the Python 3.12 static baseline and
  unsigned Swift 5/XCTest build for the local-only biometric sample.
- Added local authentication accessibility announcements for in-progress,
  success, failure, and unavailable biometric states.
- Added pinned, read-only macOS hosted project validation for the canonical
  `make check` baseline and `touchid.xcodeproj` parsing.

## 2026-06-09

- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static LocalAuthentication baseline.
- Added accessibility text for the local biometric action and in-progress
  authentication state.
- Added an in-progress title while local biometric authentication is running.

## 2026-06-08

- Removed authentication success/failure console logging from the biometric
  callback.
- Switched failure classification to use the LocalAuthentication callback error
  instead of the preflight error.
- Kept authentication results in local in-memory state with a weak callback
  capture instead of logging them.
- Made local biometric authentication explicit and user-triggered instead of
  starting automatically when the view loads.
- Classified unavailable biometric hardware and unenrolled biometric states
  without logging or remote handling.
- Added failure reason tests for unavailable Touch ID and missing
  `LocalAuthentication` errors.
- Added an error domain guard so unrelated errors are not classified as
  `LocalAuthentication` failures.
- Hid the LocalAuthentication fallback title and clarified the fallback failure
  reason so the sample does not imply an unsupported password flow.
- Updated the sample prompt to describe local authentication instead of server
  login.
- Added a POSIX-compatible `build.sh` that skips cleanly on hosts without Xcode.
- Added `make check` and a static Touch ID baseline for project metadata,
  plist/storyboard/asset parsing, LocalAuthentication flow checks, and
  local-only privacy guardrails.
