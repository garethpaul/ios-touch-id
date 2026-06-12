# Fail-Closed Authentication Result

status: completed

## Context

The LocalAuthentication completion currently reports success whenever the
framework's Boolean result is true. The documented callback contract should not
pair `success == true` with an error, but authentication UI should not announce
success if a contradictory result is ever delivered.

## Completed Scope

- Normalize completion results through a testable helper.
- Report success only when the success flag is true and the error is nil.
- Preserve specific local failure reasons for ordinary unsuccessful results.
- Add XCTest coverage for success, failure, and contradictory callback pairs.
- Extend the static baseline and documentation with the fail-closed invariant.
- Mutation-test that removing the nil-error requirement is rejected.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- `git diff --check`
- Mutation result: removing the nil-error success requirement was rejected by
  `scripts/check-baseline.py`.
