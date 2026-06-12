## iOS Touch ID Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

iOS Touch ID is a Swift sample for local biometric authentication.

The repository is useful as a compact Touch ID-era project for learning how to
request local authentication in an iOS app. Project context lives in
[`README.md`](README.md).

The goal is to keep the authentication sample small, clear, and safe around
user identity signals.

Current baseline: `make lint`, `make test`, `make build`, and `make check` run
`scripts/check-baseline.py` and compile the Swift 5 app and XCTest target when
Xcode is available. The static checks verify the Xcode project shape,
plist/storyboard/asset parsing, `LocalAuthentication` source, local biometric
wording, and authentication-state logging guardrails. The build script is
intentionally small and skips cleanly on hosts without Xcode.
The baseline also verifies that biometric prompts stay behind an explicit user
action instead of starting from `viewDidLoad`, and that unavailable biometric
states are classified locally with failure reason tests.
The error domain guard keeps unrelated errors on the generic local failure path.
The fallback title remains hidden because the sample does not implement an
alternate password flow.
The in-progress title should visibly show when local authentication is running.
The accessibility text should describe the local biometric action and in-progress
state without implying remote credential transfer.
Accessibility announcements should report local in-progress, success, and
failure states without implying remote credential transfer.

The current focus is:

Priority:

- Preserve the local authentication flow
- Keep the sample easy to build and inspect
- Keep biometric prompts explicit and user-triggered
- Keep unavailable biometric paths clear and local-only
- Keep failure reason tests focused on local error classification
- Keep the error domain guard around LocalAuthentication failure codes
- Keep the LocalAuthentication fallback title hidden unless a real fallback flow exists
- Keep the in-progress title aligned with local-only authentication state
- Keep local authentication accessibility text aligned with the local-only privacy boundary
- Keep local authentication accessibility announcements aligned with the local-only privacy boundary
- Invalidate active authentication contexts off-screen and reject stale callbacks
- Fail closed when LocalAuthentication callback success and error values conflict
- Avoid treating biometric success as remote identity proof
- Keep the sample clear that local biometric success is not server identity
  proof
- Maintain security policy, build script, and Xcode project context
- Keep `make lint`, `make test`, `make build`, and `make check` available as
  local verification gates
- Keep hosted project validation pinned and read-only on macOS, compiling the
  unsigned app and XCTest target through the canonical `make check` gate
- Keep GitHub Actions on Python 3.12 so local and hosted static checks use the
  same interpreter baseline

Next priorities:

- Add README setup and simulator/device verification notes
- Modernize from Touch ID-specific assumptions to LocalAuthentication guidance
- Add tests or manual checks for success, failure, and unavailable-biometric paths
- Document what the sample does and does not secure

Contribution rules:

- One PR = one focused authentication, UI, build, or documentation change.
- Verify on compatible hardware when changing biometric behavior.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing
  changes to authentication flow, project metadata, assets, tests, docs, or
  privacy posture.
- Keep generated signing files and local paths out of git.
- Do not add remote authentication without a separate design.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Biometric authentication should remain local and explicit. Do not log biometric
state, store sensitive secrets without keychain guidance, or use local success as
unverified server identity. The error domain guard should keep unrelated errors
out of LocalAuthentication failure reason mapping. The fallback title should stay
hidden until the sample implements an explicit fallback flow. The in-progress title
and accessibility text should keep the action and in-progress state local-only.
Accessibility announcements should keep local authentication state changes
local-only.
Hosted project validation must not invoke LocalAuthentication, access biometric
state, launch a simulator, or imply device-level coverage.

## What We Will Not Merge (For Now)

- Remote auth claims without server-side design
- Sensitive logging around authentication state
- Broad project migration mixed with authentication behavior changes
- Generated signing material

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
