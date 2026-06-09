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


REQUIRED_FILES = [
    ".gitignore",
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
    "docs/plans/2026-06-09-local-auth-error-domain.md",
    "docs/plans/2026-06-09-local-auth-fallback-title.md",
    "docs/readme-overview.svg",
    "touchid.xcodeproj/project.pbxproj",
    "touchid.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
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
    shell_result = subprocess.run(["sh", "-n", "build.sh"], cwd=str(ROOT), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if shell_result.returncode != 0:
        fail(f"build.sh must pass POSIX shell syntax checks: {shell_result.stderr.strip()}")
    for token in [
        "ci_build() {",
        'xcodebuild -project "touchid.xcodeproj"',
        '-target "touchid"',
        'ci_build "${SIMULATOR_NAME:-iPhone 6}"',
        "xcodebuild unavailable",
    ]:
        require_contains(build_script, token, "build.sh")
    if "function ci_build" in build_script:
        fail("build.sh must use POSIX function syntax")

    for token in [
        "ViewController.swift in Sources",
        "Main.storyboard in Resources",
        "Images.xcassets in Resources",
        "touchidTests.swift in Sources",
        "IPHONEOS_DEPLOYMENT_TARGET = 8.3;",
        "ENABLE_TESTABILITY = YES;",
    ]:
        require_contains(project, token, "Xcode project")
    for token in [
        "import LocalAuthentication",
        "@testable import touchid",
        "testAuthenticationFailureReasonHandlesUnavailableTouchID",
        "testAuthenticationFailureReasonHandlesMissingError",
        "testAuthenticationFailureReasonRejectsOtherErrorDomains",
        "testAuthenticationFailureReasonHandlesUserFallback",
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
        "private let authenticateButton = UIButton(type: UIButtonType.System)",
        "private var authenticationInProgress = false",
        "configureAuthenticationButton()",
        'addTarget(self, action: "authenticateButtonTapped:", forControlEvents: UIControlEvents.TouchUpInside)',
        "let context = LAContext()",
        "context.canEvaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, error: &error)",
        'context.localizedFallbackTitle = ""',
        'let reason = "Authenticate locally to continue"',
        "context.evaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics",
        "[weak self]",
        "dispatch_async(dispatch_get_main_queue())",
        "authenticationMessage",
        "authenticationFailureReason(authenticationError)",
        "func authenticationFailureReason(error: NSError?) -> String",
        "authenticationError.domain == LAErrorDomain",
        "switch authenticationError.code",
        "LAError.AuthenticationFailed.rawValue",
        "LAError.UserCancel.rawValue",
        "LAError.SystemCancel.rawValue",
        "LAError.PasscodeNotSet.rawValue",
        "LAError.UserFallback.rawValue",
        'return "user chose fallback authentication"',
        "LAError.TouchIDNotAvailable.rawValue",
        "LAError.TouchIDNotEnrolled.rawValue",
    ]:
        require_contains(source, token, "ViewController.swift")

    if "error!.code" in source:
        fail("authentication failure handling must not force-unwrap the preflight error")
    if "private func authenticationFailureReason" in source:
        fail("authenticationFailureReason must remain testable from XCTest")
    if "configureAuthenticationButton()" not in view_did_load or "authenticateWithBiometrics()" in view_did_load:
        fail("viewDidLoad must configure the explicit auth action without starting biometric authentication")
    if "authenticateWithBiometrics()" not in auth_action:
        fail("authenticateButtonTapped must start the local authentication flow")
    for token in [
        "if authenticationInProgress",
        "authenticationInProgress = true",
        "authenticationMessage = \"authentication started\"",
        "authenticateButton.enabled = false",
        "authenticationInProgress = false",
        "authenticateButton.enabled = true",
    ]:
        require_contains(auth_flow, token, "authenticateWithBiometrics")

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if re.search(pattern, source, flags=re.IGNORECASE):
            fail(f"ViewController.swift contains forbidden pattern {pattern!r}")


def check_docs() -> None:
    gitignore = read_text(".gitignore")
    for token in ["DerivedData", "*.xcuserstate", "*.local.xcconfig", "*.secrets.xcconfig", ".env"]:
        require_contains(gitignore, token, ".gitignore")

    readme = flattened(read_text("README.md"))
    for token in ["make check", "build.sh", "scripts/check-baseline.py", "LocalAuthentication", "local biometric", "authentication-state logging", "unavailable biometric", "failure reason tests", "fallback title"]:
        require_contains(readme, token, "README.md")
    require_contains(readme, "error domain guard", "README.md")

    vision = flattened(read_text("VISION.md"))
    for token in ["scripts/check-baseline.py", "build script", "local biometric", "server identity", "authentication-state logging", "unavailable biometric", "failure reason tests", "fallback title"]:
        require_contains(vision, token, "VISION.md")
    require_contains(vision, "error domain guard", "VISION.md")

    security = flattened(read_text("SECURITY.md"))
    for token in ["LocalAuthentication", "local biometric", "server identity", "make check", "authentication-state logging", "unavailable biometric", "failure reason tests", "fallback title"]:
        require_contains(security, token, "SECURITY.md")
    require_contains(security, "error domain guard", "SECURITY.md")

    changes = flattened(read_text("CHANGES.md"))
    for token in ["console logging", "callback error", "in-memory state", "explicit", "unavailable biometric", "failure reason tests", "fallback title", "build.sh", "make check", "local-only privacy"]:
        require_contains(changes, token, "CHANGES.md")
    require_contains(changes, "error domain guard", "CHANGES.md")

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


def main() -> None:
    check_required_files()
    check_project_metadata()
    check_app_metadata_and_assets()
    check_local_authentication_flow()
    check_docs()

    if not shutil.which("xcodebuild"):
        print("xcodebuild unavailable; static iOS baseline only.")

    print("ios-touch-id LocalAuthentication baseline checks passed.")


if __name__ == "__main__":
    main()
