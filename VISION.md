## iOS Touch ID Vision

iOS Touch ID is a Swift sample for local biometric authentication.

The repository is useful as a compact Touch ID-era project for learning how to
request local authentication in an iOS app. Project context lives in
[`README.md`](README.md).

The goal is to keep the authentication sample small, clear, and safe around
user identity signals.

The current focus is:

Priority:

- Preserve the local authentication flow
- Keep the sample easy to build and inspect
- Avoid treating biometric success as remote identity proof
- Maintain security policy and Xcode project context

Next priorities:

- Add README setup and simulator/device verification notes
- Modernize from Touch ID-specific assumptions to LocalAuthentication guidance
- Add tests or manual checks for success, failure, and unavailable-biometric paths
- Document what the sample does and does not secure

Contribution rules:

- One PR = one focused authentication, UI, build, or documentation change.
- Verify on compatible hardware when changing biometric behavior.
- Keep generated signing files and local paths out of git.
- Do not add remote authentication without a separate design.

## Security

Biometric authentication should remain local and explicit. Do not log biometric
state, store sensitive secrets without keychain guidance, or use local success as
unverified server identity.

## What We Will Not Merge (For Now)

- Remote auth claims without server-side design
- Sensitive logging around authentication state
- Broad project migration mixed with authentication behavior changes
- Generated signing material
