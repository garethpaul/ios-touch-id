#!/usr/bin/env python3
"""Static baseline checks for the legacy iOS Touch ID sample."""

from __future__ import annotations

import json
import plistlib
import re
import shutil
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
    "docs/plans/2026-06-08-touch-id-baseline.md",
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


def check_required_files() -> None:
    for path in REQUIRED_FILES:
        require_file(path)


def check_project_metadata() -> None:
    project = read_text("touchid.xcodeproj/project.pbxproj")
    for token in [
        "ViewController.swift in Sources",
        "Main.storyboard in Resources",
        "Images.xcassets in Resources",
        "touchidTests.swift in Sources",
        "IPHONEOS_DEPLOYMENT_TARGET = 8.3;",
    ]:
        require_contains(project, token, "Xcode project")

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
    for token in [
        "import LocalAuthentication",
        "let context = LAContext()",
        "context.canEvaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, error: &error)",
        'let reason = "Authenticate locally to continue"',
        "context.evaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics",
        "authenticationFailureReason(authenticationError)",
        "guard let code = error?.code",
        "LAError.AuthenticationFailed.rawValue",
        "LAError.UserCancel.rawValue",
        "LAError.SystemCancel.rawValue",
        "LAError.PasscodeNotSet.rawValue",
        "LAError.UserFallback.rawValue",
    ]:
        require_contains(source, token, "ViewController.swift")

    if "error!.code" in source:
        fail("authentication failure handling must not force-unwrap the preflight error")

    for pattern in FORBIDDEN_SOURCE_PATTERNS:
        if re.search(pattern, source, flags=re.IGNORECASE):
            fail(f"ViewController.swift contains forbidden pattern {pattern!r}")


def check_docs() -> None:
    gitignore = read_text(".gitignore")
    for token in ["DerivedData", "*.xcuserstate", "*.local.xcconfig", "*.secrets.xcconfig", ".env"]:
        require_contains(gitignore, token, ".gitignore")

    readme = read_text("README.md")
    for token in ["make check", "scripts/check-baseline.py", "LocalAuthentication", "local biometric", "authentication-state logging"]:
        require_contains(readme, token, "README.md")

    vision = read_text("VISION.md")
    for token in ["scripts/check-baseline.py", "local biometric", "server identity", "authentication-state", "logging guardrails"]:
        require_contains(vision, token, "VISION.md")

    security = read_text("SECURITY.md")
    for token in ["LocalAuthentication", "local biometric", "server identity", "make check", "authentication-state logging"]:
        require_contains(security, token, "SECURITY.md")

    changes = read_text("CHANGES.md")
    for token in ["console logging", "callback error", "make check", "local-only privacy"]:
        require_contains(changes, token, "CHANGES.md")

    plan = read_text("docs/plans/2026-06-08-touch-id-baseline.md")
    require_contains(plan, "status: completed", "baseline plan")


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
