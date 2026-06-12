#!/bin/sh

set -eu

if ! command -v xcodebuild >/dev/null 2>&1; then
    echo "xcodebuild unavailable; skipping Xcode build on this host."
    exit 0
fi

xcodebuild -project "touchid.xcodeproj" \
           -target "touchidTests" \
           -sdk iphonesimulator \
           -configuration "Debug" \
           CODE_SIGNING_ALLOWED=NO \
           build
