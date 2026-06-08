#!/bin/sh

set -eu

if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "xcodebuild unavailable; skipping Xcode build on this host."
    exit 0
fi

ci_build() {
    NAME=$1
    xcodebuild -project "touchid.xcodeproj" \
               -target "touchid" \
               -destination "platform=iOS Simulator,name=${NAME}" \
               -sdk iphonesimulator \
               -configuration "Debug" \
               build
}

ci_build "${SIMULATOR_NAME:-iPhone 6}"
