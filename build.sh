#!/bin/sh

set -eu

if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "xcodebuild unavailable; skipping Xcode test execution on this host."
    exit 0
fi

simulator_id=$(
    xcrun simctl list devices available --json | python3 -c '
import json
import re
import sys

devices = json.load(sys.stdin).get("devices", {})
candidates = []
for runtime, runtime_devices in devices.items():
    runtime_match = re.search(r"iOS-(\d+)(?:-(\d+))?", runtime)
    if runtime_match is None:
        continue
    version = (
        int(runtime_match.group(1)),
        int(runtime_match.group(2) or 0),
    )
    if version < (12, 0):
        continue
    for device in runtime_devices:
        if device.get("isAvailable") and device.get("name", "").startswith("iPhone"):
            booted = 1 if device.get("state") == "Booted" else 0
            candidates.append((version, booted, device["udid"]))
if candidates:
    candidates.sort()
    print(candidates[-1][2])
    raise SystemExit(0)
raise SystemExit("No available iPhone simulator was found.")
'
)

build_root=$(mktemp -d "${TMPDIR:-/tmp}/ios-touch-id-tests.XXXXXX")
cleanup_build_root() {
    rm -rf -- "$build_root"
}
trap cleanup_build_root 0 1 2 15

xcodebuild -project "touchid.xcodeproj" \
           -scheme "touchid" \
           -configuration "Debug" \
           -destination "platform=iOS Simulator,id=$simulator_id" \
           -derivedDataPath "$build_root/DerivedData" \
           CODE_SIGNING_ALLOWED=NO \
           CODE_SIGNING_REQUIRED=NO \
           test
