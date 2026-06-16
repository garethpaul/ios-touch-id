# AGENTS.md

## Repository purpose

`garethpaul/ios-touch-id` is an Apple platform application or Swift sample. TouchID Sample

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `touchid.xcodeproj` - Xcode project
- `touchid` - repository source or sample assets
- `touchidTests` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Local Apple development: `open touchid.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Swift 5 and Python 3.
- Preserve the iOS 12 deployment target and unsigned simulator build assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `docs/plans/2026-06-08-auth-failure-reason-tests.md`, `touchidTests/touchidTests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Keep signing material, local `.xcconfig` files, and environment files out of git.
- Keep the shared `touchid` scheme wired to the focused `touchidTests` target,
  and keep hosted `make check` executing those tests on an available simulator.
- Avoid authentication-state logging. Review all changes to `touchid/ViewController.swift` for fail-closed LocalAuthentication result handling, fallback behavior, explicit user-triggered prompts, and local biometric privacy.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- Run `make lint`, `make test`, `make build`, and `make check` before pushing changes to Swift sources, project metadata, storyboards, app assets, tests, or security documentation.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
