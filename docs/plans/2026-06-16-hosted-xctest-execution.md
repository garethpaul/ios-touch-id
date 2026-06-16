---
title: Hosted XCTest Execution
type: reliability
date: 2026-06-16
status: completed
execution: code
---

# Hosted XCTest Execution

## Context

The canonical macOS gate compiled the app and XCTest bundle but never executed
the eight deterministic LocalAuthentication message-mapping tests.

## Requirements

- Check in a shared scheme that includes the `touchidTests` target.
- Select an available iPhone simulator without depending on a fixed model name.
- Execute `xcodebuild test` with signing disabled and isolated DerivedData.
- Preserve a truthful static-only skip on hosts without Xcode.
- Fail static verification if the canonical gate regresses to build-only mode.

## Verification

- Repository and external-directory `make check` on Linux.
- POSIX shell, XML, project, documentation, and workflow contract checks.
- Hostile mutations for the test action, scheme, destination, cleanup, and CI
  wiring.
- Exact-head hosted push and pull-request XCTest execution before closure.

## Scope Boundary

No authentication behavior, biometric interaction, app UI, deployment target,
dependency, signing identity, or device behavior changes in this patch.
