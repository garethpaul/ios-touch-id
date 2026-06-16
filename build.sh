#!/bin/sh

set -eu

if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "xcodebuild unavailable; skipping Xcode test execution on this host."
    exit 0
fi

simulator_id=$(
    xcrun simctl list devices available --json | python3 -c '
import json
import sys

devices = json.load(sys.stdin).get("devices", {})
for runtime in sorted(devices, reverse=True):
    for device in devices[runtime]:
        if device.get("isAvailable") and device.get("name", "").startswith("iPhone"):
            print(device["udid"])
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
