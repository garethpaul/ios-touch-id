#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CHILD_MARKER = "IOS_TOUCH_ID_MAKE_SPACE_CHILD"


def run_make(make, arguments, caller, environment):
    return subprocess.run(
        [make, *arguments],
        cwd=caller,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
    )


def write_executable(path, content):
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def main():
    if os.environ.get(CHILD_MARKER) == "1":
        return

    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "-z"]
    ).decode().rstrip("\0").split("\0")
    with tempfile.TemporaryDirectory(prefix="ios-touch-id-make-space-") as temporary:
        root = Path(temporary)
        copied = root / "repository with spaces"
        caller = root / "external caller"
        shutil.copytree(
            ROOT,
            copied,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"),
        )
        caller.mkdir()
        subprocess.run(["git", "-C", copied, "init", "-q"], check=True)
        subprocess.run(
            ["git", "-C", copied, "add", "-f", "-N", "--", *tracked],
            check=True,
        )
        environment = os.environ.copy()
        environment[CHILD_MARKER] = "1"
        tool_stubs = root / "apple-tool-stubs"
        tool_stubs.mkdir()
        xcodebuild_log = root / "xcodebuild.log"
        xcrun_log = root / "xcrun.log"
        write_executable(
            tool_stubs / "xcodebuild",
            "#!/bin/sh\n"
            'printf "%s\\n" "$*" >> "$IOS_TOUCH_ID_FAKE_XCODEBUILD_LOG"\n',
        )
        write_executable(
            tool_stubs / "xcrun",
            "#!/bin/sh\n"
            'printf "%s\\n" "$*" >> "$IOS_TOUCH_ID_FAKE_XCRUN_LOG"\n'
            "cat <<'JSON'\n"
            '{"devices":{"com.apple.CoreSimulator.SimRuntime.iOS-18-5":'
            '[{"isAvailable":true,"name":"iPhone Test",'
            '"state":"Shutdown","udid":"00000000-0000-0000-0000-000000000000"}]}}\n'
            "JSON\n",
        )
        environment["IOS_TOUCH_ID_FAKE_XCODEBUILD_LOG"] = str(xcodebuild_log)
        environment["IOS_TOUCH_ID_FAKE_XCRUN_LOG"] = str(xcrun_log)
        environment["PATH"] = str(tool_stubs) + os.pathsep + environment["PATH"]
        make = environment.get("IOS_TOUCH_ID_MAKE", "make")
        repository_makefile = str(copied / "Makefile")
        subprocess.run(
            [make, "-f", repository_makefile, "check"],
            cwd=caller,
            env=environment,
            check=True,
            timeout=180,
        )
        xcodebuild_calls = xcodebuild_log.read_text(encoding="utf-8").splitlines()
        if not any(call.startswith("-list ") for call in xcodebuild_calls):
            raise RuntimeError("copied baseline must inspect the Xcode project")
        if not any(call.endswith(" test") for call in xcodebuild_calls):
            raise RuntimeError("copied build must reach the Xcode test boundary")
        if xcrun_log.read_text(encoding="utf-8").splitlines() != [
            "simctl list devices available --json"
        ]:
            raise RuntimeError("copied build must select one available simulator")

        extra_makefile = root / "extra.mk"
        extra_makefile.write_text(".PHONY: extra\nextra:\n\t@:\n", encoding="utf-8")
        replacement_makefile = root / "replacement.mk"
        replacement_makefile.write_text(".PHONY: check\ncheck:\n\t@echo BYPASSED\n", encoding="utf-8")

        preload_environment = environment.copy()
        preload_environment["MAKEFILES"] = str(extra_makefile)
        preload = run_make(make, ["-f", repository_makefile, "check"], caller, preload_environment)
        if preload.returncode == 0 or "MAKEFILES must be empty" not in preload.stderr:
            raise RuntimeError("MAKEFILES preload must fail closed")

        overridden = run_make(make, ["-f", repository_makefile, "MAKEFILE_LIST=untrusted", "check"], caller, environment)
        if overridden.returncode == 0 or "MAKEFILE_LIST must not be overridden" not in overridden.stderr:
            raise RuntimeError("MAKEFILE_LIST override must fail closed")

        for arguments in (
            ["-f", str(extra_makefile), "-f", repository_makefile, "check"],
            ["-f", repository_makefile, "-f", str(extra_makefile), "check"],
        ):
            multiple = run_make(make, arguments, caller, environment)
            if multiple.returncode == 0 or "repository Makefile must be loaded alone" not in multiple.stderr:
                raise RuntimeError("multiple loaded Makefiles must fail closed")

        replacement = run_make(
            make,
            ["-f", repository_makefile, "-f", str(replacement_makefile), "check"],
            caller,
            environment,
        )
        if replacement.returncode == 0 or "BYPASSED" in replacement.stdout:
            raise RuntimeError("later recipes must not replace repository verification")


if __name__ == "__main__":
    main()
