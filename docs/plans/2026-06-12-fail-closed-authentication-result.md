# Fail-Closed Authentication Result

status: completed

## Context

The LocalAuthentication completion currently reports success whenever the
framework's Boolean result is true. The documented callback contract should not
pair `success == true` with an error, but authentication UI should not announce
success if a contradictory result is ever delivered.

## Work Completed

- Normalize completion results through a testable helper.
- Report success only when the success flag is true and the error is nil.
- Preserve specific local failure reasons for ordinary unsuccessful results.
- Add XCTest coverage for success, failure, and contradictory callback pairs.
- Extend the static baseline and documentation with the fail-closed invariant.
- Mutation-test that removing the nil-error requirement is rejected.

## Verification Completed

- Local `make check`, `make lint`, `make test`, and `make build` passed. The
  local environment did not provide `xcodebuild`, so `build.sh` reported the
  hosted Xcode requirement after the complete static baseline passed.
- `python3 -m py_compile scripts/check-baseline.py`, `sh -n build.sh`, and
  `git diff --check` passed.
- Hostile mutations changing the plan status, inserting an unfinished-work
  marker, falsifying a run ID, removing the nil-error success requirement, or
  removing the contradictory-result regression test were rejected.
- The implementation pull-request Check run `27395341720` completed
  successfully for commit `eaaa0362c6cc9e2f0198486adefac8afa3ddf453` and
  compiled the Swift 5 authentication targets on hosted macOS.
- The post-merge push Check run `27395390267` completed successfully for
  commit `3f695c1618286e1a9e3bba7c3cf28c7a10a74a67`.
- The CodeQL setup run `27402323777` completed successfully for commit
  `3f695c1618286e1a9e3bba7c3cf28c7a10a74a67`.
- Authentication preserves `guard success, error == nil else` and XCTest
  preserves `testAuthenticationResultMessageRejectsContradictorySuccess`.
