# Changes

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
- Updated the sample prompt to describe local authentication instead of server
  login.
- Added a POSIX-compatible `build.sh` that skips cleanly on hosts without Xcode.
- Added `make check` and a static Touch ID baseline for project metadata,
  plist/storyboard/asset parsing, LocalAuthentication flow checks, and
  local-only privacy guardrails.
