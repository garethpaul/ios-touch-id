# Noninteractive Authentication Failure Reason

status: completed

## Problem

Apple documents `LAError.Code.notInteractive` for attempts where displaying the
required authentication interface is forbidden. The sample currently lets this
known LocalAuthentication result fall through to the generic unknown-error copy.

## Design

Add an explicit `.notInteractive` switch branch returning `authentication
interaction unavailable`. Preserve the LocalAuthentication error-domain guard,
fail-closed result normalization, stale-attempt rejection, and generic fallback
for missing, unrelated, or unrecognized errors.

## Test First

Add `testAuthenticationFailureReasonHandlesNotInteractive` and its static source
contract before implementation. The baseline must fail because the switch lacks
the required case.

## Verification

- `python3 scripts/check-baseline.py`
- `/usr/bin/make lint`, `/usr/bin/make test`, `/usr/bin/make build`, and
  `/usr/bin/make check` from the checkout and through the absolute Makefile path
  from `/tmp`
- One hostile mutation removing the `.notInteractive` branch
- `python3 -m py_compile scripts/check-baseline.py`
- `sh -n build.sh`
- `git diff --check`
- Local `xcodebuild` is unavailable; hosted macOS CI executes focused XCTest.

The red-first contract failed on the missing switch branch. The completed
implementation passed every Make alias, the checkout and absolute-Makefile
gates, four bundle-identifier mutations, the isolated hostile branch-removal
mutation, Python compilation, shell syntax, and `git diff --check`.

## Scope Boundaries

- Authentication policy, prompts, fallback visibility, context ownership,
  success validation, accessibility, privacy, bundle metadata, deployment
  target, and stale completion handling are unchanged.
- Unknown codes and non-LocalAuthentication domains remain generic and fail closed.

## Reference

- https://developer.apple.com/documentation/localauthentication/laerror-swift.struct/code/notinteractive
