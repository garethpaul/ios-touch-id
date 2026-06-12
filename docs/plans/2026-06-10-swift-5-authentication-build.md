# Swift 5 Authentication Build

status: completed

## Problem

The app and tests use Swift 2-era UIKit and LocalAuthentication APIs and target
iOS 8.3. Hosted validation only parses the project, so source and XCTest
compatibility are not compiler-verified on current Xcode.

## Scope

- Migrate app, authentication controller, and XCTest source to Swift 5.
- Preserve explicit biometric-only authentication, hidden fallback, local-only
  messages, and accessibility status announcements.
- Invalidate the active authentication context when the screen disappears and
  ignore stale completion callbacks.
- Map current LocalAuthentication biometric error cases without force unwraps.
- Raise deployment settings to iOS 12 and set Swift 5 for every configuration.
- Compile the XCTest target through the canonical `make check` gate on macOS.
- Extend the static baseline to guard the modern security and build contracts.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- XCTest target build on hosted Xcode
- mutation checks for stale-callback and compiler-gate regressions
- `git diff --check`
