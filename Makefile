.PHONY: build check lint test

override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
export ROOT

lint test build: check

check:
	python3 "$$ROOT/scripts/check-baseline.py"
	cd "$$ROOT" && ./build.sh
