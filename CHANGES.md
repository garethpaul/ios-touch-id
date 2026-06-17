# Changes

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
