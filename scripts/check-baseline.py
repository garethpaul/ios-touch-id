#!/usr/bin/env python3
"""Static baseline checks for the legacy iOS Touch ID sample."""

from __future__ import annotations

import json
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FACE_ID_USAGE_DESCRIPTION = "Use Face ID to authenticate locally on this device."


REQUIRED_FILES = [
    ".gitignore",
    ".github/workflows/check.yml",
    "CHANGES.md",
    "Makefile",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "build.sh",
    "docs/plans/2026-06-08-explicit-local-auth.md",
    "docs/plans/2026-06-08-auth-failure-reason-tests.md",
    "docs/plans/2026-06-08-local-auth-unavailable-reasons.md",
    "docs/plans/2026-06-08-touch-id-baseline.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
    "docs/plans/2026-06-09-local-auth-error-domain.md",
    "docs/plans/2026-06-09-local-auth-fallback-title.md",
    "docs/plans/2026-06-09-local-auth-accessibility.md",
    "docs/plans/2026-06-09-local-auth-in-progress-title.md",
    "docs/plans/2026-06-10-local-auth-accessibility-announcements.md",
    "docs/plans/2026-06-10-ci-baseline.md",
    "docs/plans/2026-06-10-hosted-project-validation.md",
    "docs/plans/2026-06-10-swift-5-authentication-build.md",
    "docs/plans/2026-06-12-fail-closed-authentication-result.md",
    "docs/plans/2026-06-13-completed-auth-context-invalidation.md",
    "docs/plans/2026-06-13-location-independent-make.md",
    "docs/plans/2026-06-16-hosted-xctest-execution.md",
    "docs/plans/2026-06-17-019-add-face-id-usage-description-plan.md",
    "docs/plans/2026-06-18-biometric-neutral-failure-copy.md",
    "docs/readme-overview.svg",
    "touchid.xcodeproj/project.pbxproj",
    "touchid.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
    "touchid.xcodeproj/xcshareddata/xcschemes/touchid.xcscheme",
    "touchid/AppDelegate.swift",
    "touchid/Base.lproj/LaunchScreen.xib",
    "touchid/Base.lproj/Main.storyboard",
    "touchid/Images.xcassets/AppIcon.appiconset/Contents.json",
    "touchid/Info.plist",
    "touchid/ViewController.swift",
    "touchidTests/Info.plist",
    "touchidTests/touchidTests.swift",
]


FORBIDDEN_SOURCE_PATTERNS = [
    r"\bprint\s*\(",
    r"\bprintln\s*\(",
    r"\bNSLog\s*\(",
    r"\bNSURL\b",
    r"\bURLSession\b",
    r"\bNSURLConnection\b",
    r"http://",
    r"https://",
    r"\bserver login\b",
    r"\banalytics\b",
    r"\bupload\b",
    r"\btoken\b",
    r"\bsecret\b",
]


def fail(message: str) -> None:
    print(f"check-baseline: {message}", file=sys.stderr)
    sys.exit(1)


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require_file(path: str) -> Path:
    candidate = ROOT / path
    if not candidate.is_file():
        fail(f"missing required file: {path}")
    return candidate


def require_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        fail(f"{label} must mention {needle!r}")


def flattened(text: str) -> str:
    return " ".join(text.split())


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def parse_xml(path: str) -> ET.Element:
    try:
        return ET.parse(ROOT / path).getroot()
    except ET.ParseError as exc:
        fail(f"{path} is not valid XML: {exc}")


def parse_json(path: str) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON: {exc}")


def parse_plist(path: str) -> object:
    try:
        with (ROOT / path).open("rb") as fh:
            return plistlib.load(fh)
    except Exception as exc:
        fail(f"{path} is not a valid plist: {exc}")


def strip_swift_line_comments(text: str) -> str:
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


def swift_function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start == -1:
        return ""

    body_start = text.find("{", start)
    if body_start == -1:
        return ""

    depth = 0
    for index in range(body_start, len(text)):
        character = text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[body_start + 1:index]
    return ""


def check_required_files() -> None:
    for path in REQUIRED_FILES:
        require_file(path)


def check_project_metadata() -> None:
    project = read_text("touchid.xcodeproj/project.pbxproj")
    tests = read_text("touchidTests/touchidTests.swift")
    build_script = read_text("build.sh")
    scheme = read_text("touchid.xcodeproj/xcshareddata/xcschemes/touchid.xcscheme")
    shell_result = subprocess.run(["sh", "-n", "build.sh"], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if shell_result.returncode != 0:
        fail(f"build.sh must pass POSIX shell syntax checks: {shell_result.stderr.strip()}")
    for token in [
        'xcodebuild -project "touchid.xcodeproj"',
        '-scheme "touchid"',
        '-destination "platform=iOS Simulator,id=$simulator_id"',
        '-derivedDataPath "$build_root/DerivedData"',
        'configuration "Debug"',
        "CODE_SIGNING_ALLOWED=NO",
        "CODE_SIGNING_REQUIRED=NO",
        "xcrun simctl list devices available --json",
        "runtime_match = re.search",
        r"iOS-(\d+)(?:-(\d+))?",
        'startswith("iPhone")',
        'device.get("state") == "Booted"',
        'build_root=$(mktemp -d "${TMPDIR:-/tmp}/ios-touch-id-tests.XXXXXX")',
        "trap cleanup_build_root 0 1 2 15",
        "test",
        "xcodebuild unavailable",
    ]:
        require_contains(build_script, token, "build.sh")
    if "function ci_build" in build_script:
        fail("build.sh must use POSIX function syntax")
    if "-target \"touchidTests\"" in build_script or build_script.rstrip().endswith("build"):
        fail("build.sh must execute XCTest instead of compiling the test target only")
    if "sorted(devices, reverse=True)" in build_script:
        fail("build.sh must select simulator runtimes by parsed iOS version, not lexicographic runtime names")

    scheme_root = parse_xml("touchid.xcodeproj/xcshareddata/xcschemes/touchid.xcscheme")
    if scheme_root.tag != "Scheme":
        fail("touchid.xcscheme must describe an Xcode scheme")
    for token in [
        'BlueprintIdentifier = "7F2332C81B119134000AF54B"',
        'BlueprintIdentifier = "7F2332DD1B119134000AF54B"',
        'BuildableName = "touchidTests.xctest"',
        '<TestAction',
        '<TestableReference',
        'skipped = "NO"',
    ]:
        require_contains(scheme, token, "touchid.xcscheme")

    for token in [
        "ViewController.swift in Sources",
        "Main.storyboard in Resources",
        "Images.xcassets in Resources",
        "touchidTests.swift in Sources",
        "ENABLE_TESTABILITY = YES;",
    ]:
        require_contains(project, token, "Xcode project")
    if project.count("IPHONEOS_DEPLOYMENT_TARGET = 12.0;") != 2:
        fail("Xcode project must use iOS 12 for both project configurations")
    if project.count("SWIFT_VERSION = 5.0;") != 6:
        fail("Xcode project must use Swift 5 for every project and target configuration")
    for token in [
        "import LocalAuthentication",
        "@testable import touchid",
        "testAuthenticationFailureReasonHandlesUnavailableBiometrics",
        "testAuthenticationFailureReasonHandlesUnenrolledBiometrics",
        "testAuthenticationFailureReasonHandlesMissingError",
        "testAuthenticationFailureReasonRejectsOtherErrorDomains",
        "testAuthenticationFailureReasonHandlesUserFallback",
        "testAuthenticationFailureReasonHandlesBiometryLockout",
        "testAuthenticationFailureReasonHandlesUserCancel",
        "testAuthenticationFailureReasonHandlesSystemCancel",
        "testAuthenticationFailureReasonHandlesPasscodeNotSet",
        "testAuthenticationFailureReasonHandlesUnknownLocalAuthenticationError",
        "testAuthenticationResultMessageHandlesSuccessfulResult",
        "testAuthenticationResultMessageHandlesFailedResult",
        "testAuthenticationResultMessageRejectsContradictorySuccess",
        "testAuthenticationResultMessageRejectsMissingErrorFailure",
        'authenticationResultMessage(success: true, error: error), "authentication failed"',
        'authenticationResultMessage(success: false, error: nil), "unable to authenticate user"',
        "LAError.errorDomain",
        "LAError.Code.biometryNotAvailable.rawValue",
        "LAError.Code.userCancel.rawValue",
        "LAError.Code.systemCancel.rawValue",
        "LAError.Code.passcodeNotSet.rawValue",
        "XCTAssertEqual",
    ]:
        require_contains(tests, token, "touchidTests.swift")
    if "XCTAssert(true" in tests or "testPerformanceExample" in tests:
        fail("touchidTests.swift must replace template tests with authentication failure reason assertions")

    workspace = parse_xml("touchid.xcodeproj/project.xcworkspace/contents.xcworkspacedata")
    if workspace.tag != "Workspace":
        fail("contents.xcworkspacedata must describe an Xcode workspace")


def check_app_metadata_and_assets() -> None:
    info = parse_plist("touchid/Info.plist")
    if info.get("CFBundlePackageType") != "APPL":
        fail("touchid Info.plist must describe an app bundle")
    if info.get("UIMainStoryboardFile") != "Main":
        fail("touchid Info.plist must point at Main.storyboard")
    if info.get("UILaunchStoryboardName") != "LaunchScreen":
        fail("touchid Info.plist must point at LaunchScreen")
    face_id_description = info.get("NSFaceIDUsageDescription")
    if not isinstance(face_id_description, str) or face_id_description.strip() != FACE_ID_USAGE_DESCRIPTION:
        fail("touchid Info.plist must explain that Face ID authenticates locally on this device")

    tests = parse_plist("touchidTests/Info.plist")
    if tests.get("CFBundlePackageType") != "BNDL":
        fail("touchidTests Info.plist must describe a test bundle")

    storyboard = read_text("touchid/Base.lproj/Main.storyboard")
    require_contains(storyboard, 'customClass="ViewController"', "Main.storyboard")
    parse_xml("touchid/Base.lproj/Main.storyboard")
    parse_xml("touchid/Base.lproj/LaunchScreen.xib")
    parse_xml("docs/readme-overview.svg")

    app_icons = parse_json("touchid/Images.xcassets/AppIcon.appiconset/Contents.json")
    images = app_icons.get("images", []) if isinstance(app_icons, dict) else []
    if len(images) < 12:
        fail("AppIcon Contents.json must keep the iPhone/iPad icon slots")


def check_local_authentication_flow() -> None:
    source = strip_swift_line_comments(read_text("touchid/ViewController.swift"))
    view_did_load = swift_function_body(source, "override func viewDidLoad")
    auth_action = swift_function_body(source, "func authenticateButtonTapped")
    auth_flow = swift_function_body(source, "func authenticateWithBiometrics")
    for token in [
        "import LocalAuthentication",
        "private let authenticateButton = UIButton(type: .system)",
        "private var authenticationInProgress = false",
        "private var authenticationContext: LAContext?",
        "private var authenticationAttempt: UUID?",
        "configureAuthenticationButton()",
        "private func describeReadyAuthenticationButton()",
        'authenticateButton.setTitle("Authenticate Locally", for: .normal)',
        'authenticateButton.accessibilityLabel = "Authenticate Locally"',
        'authenticateButton.accessibilityHint = "Starts local biometric authentication without sending credentials"',
        'authenticateButton.setTitle("Authenticating...", for: .disabled)',
        'authenticateButton.accessibilityLabel = "Authenticating Locally"',
        'authenticateButton.accessibilityHint = "Local biometric authentication is in progress"',
        "private func announceAuthenticationStatus(_ message: String)",
        "UIAccessibility.post(notification: .announcement, argument: message)",
        'announceAuthenticationStatus("Authenticating Locally")',
        "addTarget(self, action: #selector(authenticateButtonTapped(_:)), for: .touchUpInside)",
        "let context = LAContext()",
        "let attempt = UUID()",
        "authenticationContext = context",
        "authenticationAttempt = attempt",
        "context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)",
        'context.localizedFallbackTitle = ""',
        "context.evaluatePolicy(",
        ".deviceOwnerAuthenticationWithBiometrics",
        'localizedReason: "Authenticate locally to continue"',
        "[weak self]",
        "DispatchQueue.main.async",
        "authenticationMessage",
        "authenticationResultMessage(",
        "success: success",
        "error: authenticationError",
        "finishAuthentication(attempt: attempt, message: message)",
        "private func finishAuthentication(attempt: UUID, message: String)",
        "guard authenticationAttempt == attempt",
        "authenticationContext = nil",
        "func authenticationResultMessage(success: Bool, error: Error?) -> String",
        "guard success, error == nil else",
        "return authenticationFailureReason(error)",
        'return "authentication succeeded"',
        "func authenticationFailureReason(_ error: Error?) -> String",
        "guard let error = error",
        "let authenticationError = error as NSError",
        "authenticationError.domain == LAError.errorDomain",
        "LAError.Code(rawValue: authenticationError.code)",
        "switch code",
        "case .authenticationFailed:",
        "case .userCancel:",
        "case .systemCancel:",
        "case .passcodeNotSet:",
        "case .userFallback:",
        'return "user chose fallback authentication"',
        "case .biometryNotAvailable:",
        "case .biometryNotEnrolled:",
        "case .biometryLockout:",
        'return "biometric authentication unavailable"',
        'return "biometric authentication not enrolled"',
        'return "biometric authentication locked"',
    ]:
        require_contains(source, token, "ViewController.swift")

    tests = read_text("touchidTests/touchidTests.swift")
    for token in [
        "testAuthenticationFailureReasonHandlesUnavailableBiometrics",
        "testAuthenticationFailureReasonHandlesUnenrolledBiometrics",
        "testAuthenticationFailureReasonHandlesBiometryLockout",
        "testAuthenticationFailureReasonHandlesUserCancel",
        "testAuthenticationFailureReasonHandlesSystemCancel",
        "testAuthenticationFailureReasonHandlesPasscodeNotSet",
        "testAuthenticationFailureReasonHandlesUnknownLocalAuthenticationError",
        "testAuthenticationResultMessageRejectsMissingErrorFailure",
        '"biometric authentication unavailable"',
        '"biometric authentication not enrolled"',
        '"biometric authentication locked"',
        '"user canceled authentication"',
        '"system canceled authentication"',
        '"passcode not set"',
        '"unable to authenticate user"',
    ]:
        require_contains(tests, token, "touchidTests.swift")
    for stale_copy in ["touch id unavailable", "touch id not enrolled", "touch id locked"]:
        if stale_copy in source.lower() or stale_copy in tests.lower():
            fail(f"LocalAuthentication source and tests must not retain stale sensor-specific copy: {stale_copy}")

    if "error!.code" in source:
        fail("authentication failure handling must not force-unwrap the preflight error")
    if "private func authenticationFailureReason" in source:
        fail("authenticationFailureReason must remain testable from XCTest")
    if "configureAuthenticationButton()" not in view_did_load or "authenticateWithBiometrics()" in view_did_load:
        fail("viewDidLoad must configure the explicit auth action without starting biometric authentication")
    if "authenticateWithBiometrics()" not in auth_action:
        fail("authenticateButtonTapped must start the local authentication flow")
    view_did_disappear = swift_function_body(source, "override func viewDidDisappear")
    for token in ["authenticationAttempt = nil", "authenticationContext?.invalidate()", "authenticationContext = nil"]:
        require_contains(view_did_disappear, token, "viewDidDisappear")
    finish_authentication = swift_function_body(source, "private func finishAuthentication")
    finish_tokens = [
        "guard authenticationAttempt == attempt",
        "authenticationContext?.invalidate()",
        "authenticationAttempt = nil",
        "authenticationContext = nil",
        "authenticationInProgress = false",
        "authenticateButton.isEnabled = true",
        "describeReadyAuthenticationButton()",
        "authenticationMessage = message",
        "announceAuthenticationStatus(message)",
    ]
    finish_positions = [finish_authentication.find(token) for token in finish_tokens]
    if any(position == -1 for position in finish_positions) or finish_positions != sorted(finish_positions):
        fail("finishAuthentication must validate the attempt, invalidate its context, clear state, restore UI, and announce in order")
    for token in [
        "guard !authenticationInProgress",
        "authenticationInProgress = true",
        "authenticationMessage = \"authentication started\"",
        "authenticateButton.setTitle(\"Authenticating...\", for: .disabled)",
        "authenticateButton.isEnabled = false",
        "authenticateButton.accessibilityLabel = \"Authenticating Locally\"",
        "authenticateButton.accessibilityHint = \"Local biometric authentication is in progress\"",
    ]:
        require_contains(auth_flow, token, "authenticateWithBiometrics")
    in_progress_title_index = auth_flow.find('authenticateButton.setTitle("Authenticating...", for: .disabled)')
    disable_button_index = auth_flow.find("authenticateButton.isEnabled = false", in_progress_title_index)
    if in_progress_title_index == -1 or disable_button_index == -1 or in_progress_title_index > disable_button_index:
        fail("authenticateWithBiometrics must set the disabled in-progress title before disabling the button")

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if re.search(pattern, source, flags=re.IGNORECASE):
            fail(f"ViewController.swift contains forbidden pattern {pattern!r}")


def check_docs() -> None:
    makefile = read_text("Makefile")
    for token in [
        ".PHONY: build check lint test",
        "override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))",
        "export ROOT",
        "lint test build: check",
        'check:\n\tpython3 "$$ROOT/scripts/check-baseline.py"\n\tcd "$$ROOT" && ./build.sh',
    ]:
        require_contains(makefile, token, "Makefile")
    if (
        "python3 scripts/check-baseline.py" in makefile
        or "\n\t./build.sh" in makefile
        or 'python3 "$(ROOT)/scripts/check-baseline.py"' in makefile
        or 'cd "$(ROOT)" && ./build.sh' in makefile
    ):
        fail("Makefile contains caller-relative verification commands")

    workflow = read_text(".github/workflows/check.yml")
    for token in [
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "persist-credentials: false",
        "Validate baseline and execute XCTest",
        "make check",
    ]:
        require_contains(workflow, token, "GitHub Actions workflow")

    gitignore = read_text(".gitignore")
    for token in ["DerivedData", "*.xcuserstate", "*.local.xcconfig", "*.secrets.xcconfig", ".env"]:
        require_contains(gitignore, token, ".gitignore")

    readme = flattened(read_text("README.md"))
    for token in ["make lint", "make test", "make build", "make check", "GitHub Actions", "build.sh", "scripts/check-baseline.py", "LocalAuthentication", "local biometric", "authentication-state logging", "unavailable biometric", "failure reason tests", "fallback title", "accessibility", "terminal context invalidation"]:
        require_contains(readme, token, "README.md")
    require_contains(readme, "error domain guard", "README.md")
    require_contains(readme, "in-progress title", "README.md")
    require_contains(readme, "accessibility announcements", "README.md")
    require_contains(readme, "macos-15", "README.md")
    require_contains(readme, "executes all focused Swift 5 XCTest cases", "README.md")
    require_contains(readme, "available iPhone simulator", "README.md")
    require_contains(readme, "Face ID usage description", "README.md")
    require_contains(readme, "local and on-device", "README.md")
    if "unavailable touch id" in readme.lower():
        fail("README.md must describe unavailable biometrics without stale Touch ID-specific wording")

    vision = flattened(read_text("VISION.md"))
    for token in ["scripts/check-baseline.py", "make lint", "make test", "make build", "GitHub Actions", "build script", "local biometric", "server identity", "authentication-state logging", "unavailable biometric", "failure reason tests", "fallback title", "accessibility", "terminal context invalidation"]:
        require_contains(vision, token, "VISION.md")
    require_contains(vision, "error domain guard", "VISION.md")
    require_contains(vision, "in-progress title", "VISION.md")
    require_contains(vision, "accessibility announcements", "VISION.md")
    require_contains(vision, "hosted project validation", "VISION.md")
    require_contains(vision, "execute the Swift 5 XCTest target", "VISION.md")
    require_contains(vision, "Face ID usage description", "VISION.md")
    require_contains(vision, "local and on-device", "VISION.md")

    security = flattened(read_text("SECURITY.md"))
    for token in ["LocalAuthentication", "local biometric", "server identity", "make check", "GitHub Actions", "authentication-state logging", "unavailable biometric", "failure reason tests", "fallback title", "accessibility", "terminal context invalidation"]:
        require_contains(security, token, "SECURITY.md")
    require_contains(security, "error domain guard", "SECURITY.md")
    require_contains(security, "in-progress title", "SECURITY.md")
    require_contains(security, "accessibility announcements", "SECURITY.md")
    require_contains(security, "read-only", "SECURITY.md")
    require_contains(security, "stale completion callbacks", "SECURITY.md")
    require_contains(security, "executes the unsigned focused XCTest target", "SECURITY.md")
    require_contains(security, "Face ID usage description", "SECURITY.md")
    require_contains(security, "local and on-device", "SECURITY.md")
    if "simulator compilation" in security.lower():
        fail("SECURITY.md must describe XCTest execution, not stale simulator compilation")

    changes = flattened(read_text("CHANGES.md"))
    for token in ["GitHub Actions", "console logging", "callback error", "in-memory state", "explicit", "unavailable biometric", "failure reason tests", "fallback title", "accessibility", "build.sh", "make lint", "make test", "make build", "make check", "local-only privacy", "terminal context invalidation"]:
        require_contains(changes, token, "CHANGES.md")
    require_contains(changes, "error domain guard", "CHANGES.md")
    require_contains(changes, "in-progress title", "CHANGES.md")
    require_contains(changes, "accessibility announcements", "CHANGES.md")
    require_contains(changes, "hosted project validation", "CHANGES.md")
    require_contains(changes, "Swift 5", "CHANGES.md")
    require_contains(changes, "stale completion callbacks", "CHANGES.md")
    require_contains(changes, "instead of compiling the test target only", "CHANGES.md")
    require_contains(changes, "Face ID usage description", "CHANGES.md")
    require_contains(changes, "local and on-device", "CHANGES.md")

    agent_guidance = flattened(read_text("AGENTS.md"))
    for document_name, document in [
        ("README.md", readme),
        ("VISION.md", vision),
        ("SECURITY.md", security),
        ("CHANGES.md", changes),
        ("AGENTS.md", agent_guidance),
    ]:
        require_contains(document, "biometric-neutral failure copy", document_name)

    neutral_copy_plan = read_text("docs/plans/2026-06-18-biometric-neutral-failure-copy.md")
    neutral_copy_statuses = re.findall(r"(?mi)^status:\s*(.+?)\s*$", neutral_copy_plan)
    neutral_copy_verification = markdown_section(neutral_copy_plan, "Verification Completed")
    neutral_copy_required = [
        "All four Make gates",
        "absolute Makefile",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n build.sh",
        "Seven isolated hostile mutations",
        "git diff --check",
        "xcodebuild was unavailable",
    ]
    if not (
        neutral_copy_statuses == ["completed"]
        and all(token in neutral_copy_verification for token in neutral_copy_required)
        and re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", neutral_copy_verification) is None
    ):
        fail("biometric-neutral failure-copy plan must record completed verification")

    face_id_plan = read_text("docs/plans/2026-06-17-019-add-face-id-usage-description-plan.md")
    for token in [
        "title: Face ID Usage Description",
        "type: fix",
        "date: 2026-06-17",
        "R1.",
        "R6.",
        "NSFaceIDUsageDescription",
    ]:
        require_contains(face_id_plan, token, "Face ID usage description plan")
    if re.search(r"(?mi)^status:\s*", face_id_plan):
        fail("Face ID usage description plan must use modern metadata without a legacy status field")

    hosted_xctest_plan = flattened(read_text("docs/plans/2026-06-16-hosted-xctest-execution.md"))
    for token in [
        "status: completed",
        "shared scheme",
        "available iPhone simulator",
        "xcodebuild test",
        "signing disabled",
        "isolated DerivedData",
        "hosts without Xcode",
        "hosted push and pull-request XCTest execution before closure",
    ]:
        require_contains(hosted_xctest_plan, token, "hosted XCTest execution plan")

    make_gates_plan = flattened(read_text("docs/plans/2026-06-09-make-gate-aliases.md"))
    require_contains(make_gates_plan, "status: completed", "make gate aliases plan")
    plan = flattened(read_text("docs/plans/2026-06-08-touch-id-baseline.md"))
    require_contains(plan, "status: completed", "baseline plan")
    explicit_plan = flattened(read_text("docs/plans/2026-06-08-explicit-local-auth.md"))
    require_contains(explicit_plan, "status: completed", "explicit auth plan")
    unavailable_plan = flattened(read_text("docs/plans/2026-06-08-local-auth-unavailable-reasons.md"))
    require_contains(unavailable_plan, "status: completed", "unavailable auth plan")
    failure_reason_plan = flattened(read_text("docs/plans/2026-06-08-auth-failure-reason-tests.md"))
    require_contains(failure_reason_plan, "status: completed", "failure reason test plan")
    error_domain_plan = flattened(read_text("docs/plans/2026-06-09-local-auth-error-domain.md"))
    require_contains(error_domain_plan, "status: completed", "error domain plan")
    fallback_title_plan = flattened(read_text("docs/plans/2026-06-09-local-auth-fallback-title.md"))
    require_contains(fallback_title_plan, "status: completed", "fallback title plan")
    accessibility_plan = flattened(read_text("docs/plans/2026-06-09-local-auth-accessibility.md"))
    require_contains(accessibility_plan, "status: completed", "accessibility plan")
    in_progress_title_plan = flattened(read_text("docs/plans/2026-06-09-local-auth-in-progress-title.md"))
    require_contains(in_progress_title_plan, "status: completed", "in-progress title plan")
    accessibility_announcements_plan = flattened(read_text("docs/plans/2026-06-10-local-auth-accessibility-announcements.md"))
    require_contains(accessibility_announcements_plan, "status: completed", "accessibility announcements plan")
    fail_closed_result_plan = read_text("docs/plans/2026-06-12-fail-closed-authentication-result.md")
    fail_closed_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", fail_closed_result_plan)
    fail_closed_work = markdown_section(fail_closed_result_plan, "Work Completed")
    fail_closed_verification = markdown_section(
        fail_closed_result_plan, "Verification Completed"
    )
    if fail_closed_status != ["completed"] or not fail_closed_work:
        fail("fail-closed authentication result plan must record one completed status and completed work")
    if not fail_closed_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", fail_closed_verification
    ):
        fail("fail-closed authentication result plan must record finished verification without pending markers")
    for evidence in [
        "make check",
        "make lint",
        "make test",
        "make build",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n build.sh",
        "git diff --check",
        "27395341720",
        "27395390267",
        "27402323777",
        "eaaa0362c6cc9e2f0198486adefac8afa3ddf453",
        "3f695c1618286e1a9e3bba7c3cf28c7a10a74a67",
        "guard success, error == nil else",
        "testAuthenticationResultMessageRejectsContradictorySuccess",
    ]:
        require_contains(fail_closed_verification, evidence, "fail-closed authentication result plan")
    completed_context_plan = read_text("docs/plans/2026-06-13-completed-auth-context-invalidation.md")
    require_contains(completed_context_plan, "status: completed", "completed authentication context plan")
    require_contains(completed_context_plan, "All four Make gates", "completed authentication context plan")
    require_contains(completed_context_plan.lower(), "hostile mutations", "completed authentication context plan")
    location_make_plan = read_text("docs/plans/2026-06-13-location-independent-make.md")
    location_make_statuses = re.findall(r"^status: .+$", location_make_plan, flags=re.MULTILINE)
    location_make_verification = markdown_section(location_make_plan, "Verification Completed")
    if not (
        location_make_statuses == ["status: completed"]
        and "All four Make gates passed from the checkout" in location_make_verification
        and "All four Make gates passed from `/tmp` through the absolute Makefile path" in location_make_verification
        and "python3 -m py_compile scripts/check-baseline.py" in location_make_verification
        and "sh -n build.sh" in location_make_verification
        and "project metadata parsing" in location_make_verification
        and "git diff --check" in location_make_verification
        and "`xcodebuild` was unavailable" in location_make_verification
        and "Six isolated hostile mutations were rejected" in location_make_verification
        and re.search(r"\b(?:pending|todo|tbd|not run)\b", location_make_verification, re.IGNORECASE) is None
    ):
        fail("location-independent Make plan must record completed status and actual local verification")
    readme = read_text("README.md").lower()
    changes = read_text("CHANGES.md").lower()
    require_contains(readme, "absolute makefile path", "README")
    require_contains(changes, "location-independent", "CHANGES")
    ci_plan = flattened(read_text("docs/plans/2026-06-10-ci-baseline.md"))
    require_contains(ci_plan, "status: completed", "CI baseline plan")
    require_contains(ci_plan, "GitHub Actions", "CI baseline plan")
    require_contains(ci_plan, "make check", "CI baseline plan")
    hosted_validation_plan = flattened(read_text("docs/plans/2026-06-10-hosted-project-validation.md"))
    require_contains(hosted_validation_plan, "status: completed", "hosted project validation plan")
    swift_5_plan = flattened(read_text("docs/plans/2026-06-10-swift-5-authentication-build.md"))
    require_contains(swift_5_plan, "status: completed", "Swift 5 authentication build plan")


def check_hosted_validation() -> None:
    workflow = read_text(".github/workflows/check.yml")
    for token in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: macos-15",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "persist-credentials: false",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "run: make check",
    ]:
        require_contains(workflow, token, ".github/workflows/check.yml")

    if workflow.count("permissions:") != 1:
        fail("GitHub Actions must define exactly one permissions block")
    if re.search(r"^\s+[A-Za-z-]+:\s+write\s*$", workflow, flags=re.MULTILINE):
        fail("GitHub Actions permissions must remain read-only")

    actions = re.findall(r"^\s*(?:-\s*)?uses:\s*(\S+)\s*$", workflow, flags=re.MULTILINE)
    expected_actions = [
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
    ]
    if actions != expected_actions:
        fail("GitHub Actions must use only the expected pinned checkout and Python actions")
    if workflow.count("persist-credentials: false") != 1:
        fail("GitHub Actions checkout must disable credential persistence exactly once")

    if shutil.which("xcodebuild"):
        result = subprocess.run(
            ["xcodebuild", "-list", "-project", "touchid.xcodeproj"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            fail("xcodebuild could not parse touchid.xcodeproj: " + result.stderr.strip())
    else:
        print("xcodebuild unavailable; static iOS baseline only.")


def main() -> None:
    check_required_files()
    check_project_metadata()
    check_app_metadata_and_assets()
    check_local_authentication_flow()
    check_docs()
    check_hosted_validation()

    print("ios-touch-id LocalAuthentication baseline checks passed.")


if __name__ == "__main__":
    main()
