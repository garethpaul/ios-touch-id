#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PATH = Path("touchid.xcodeproj/project.pbxproj")
MUTATIONS = {
    "app debug": ("7F2332E91B119134000AF54B", "com.garethpaul.touchid"),
    "app release": ("7F2332EA1B119134000AF54B", "com.garethpaul.touchid"),
    "tests debug": ("7F2332EC1B119134000AF54B", "com.garethpaul.touchidTests"),
    "tests release": ("7F2332ED1B119134000AF54B", "com.garethpaul.touchidTests"),
}


def configuration_settings(project: str, configuration_id: str) -> tuple[int, int]:
    configuration_start = project.find(f"{configuration_id} /* ")
    settings_start = project.find("buildSettings = {", configuration_start)
    settings_end = project.find("\n\t\t\t};", settings_start)
    if min(configuration_start, settings_start, settings_end) < 0:
        raise ValueError(f"missing configuration fixture: {configuration_id}")
    return settings_start, settings_end


def main() -> int:
    baseline = subprocess.run(
        [sys.executable, "scripts/check-baseline.py"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if baseline.returncode != 0:
        print("unmutated bundle identifier baseline must pass", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="ios-touch-id-bundle-identifiers-") as directory:
        for description, (configuration_id, bundle_identifier) in MUTATIONS.items():
            mutation_root = Path(directory) / description.replace(" ", "-")
            shutil.copytree(
                ROOT,
                mutation_root,
                ignore=shutil.ignore_patterns(".git", "build", "DerivedData", "*.xcresult"),
            )
            project_path = mutation_root / PROJECT_PATH
            project = project_path.read_text(encoding="utf-8")
            settings_start, settings_end = configuration_settings(project, configuration_id)
            settings = project[settings_start:settings_end]
            original = f"PRODUCT_BUNDLE_IDENTIFIER = {bundle_identifier};"
            if settings.count(original) != 1:
                print(f"mutation fixture mismatch: {description}", file=sys.stderr)
                return 1
            mutated_settings = settings.replace(
                original,
                "PRODUCT_BUNDLE_IDENTIFIER = com.garethpaul.MismatchedIdentifier;",
                1,
            )
            project_path.write_text(
                project[:settings_start] + mutated_settings + project[settings_end:],
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "scripts/check-baseline.py"],
                cwd=mutation_root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                print(f"baseline accepted bundle identifier mutation: {description}", file=sys.stderr)
                return 1

    print(f"Rejected {len(MUTATIONS)} target bundle identifier mutations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
