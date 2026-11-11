#!/usr/bin/env python3
"""Check the preliminary garnet UEFI patch without modifying the checkout."""

import argparse
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/uefi/0001-garnet-unixnu-handoff.patch"
SUPPORTED = {
    "f8779ea0bfb33e2aec31da4a902b4a4eb8abd044": "garnet-linux reference",
    "425ed9ad8c78f8cee48886be1f9ed1e74d4e0b55": "JosephMontfort reference",
}
FILES = (
    "Platforms/Xiaomi/garnetPkg/garnet.dsc",
    "Platforms/Xiaomi/garnetPkg/garnet.fdf",
    "Platforms/Xiaomi/garnetPkg/Include/DXE.inc",
    "Silicon/Silicium/SiliciumPkg/SiliciumPkg.dsc.inc",
)


def git(uefi, *args):
    return subprocess.run(
        ["git", "-C", str(uefi), *args], capture_output=True, text=True, check=False,
    )


def check(uefi):
    revision = git(uefi, "rev-parse", "HEAD")
    if revision.returncode or revision.stdout.strip() not in SUPPORTED:
        return False, "Unsupported or unreadable UEFI revision; inspect and pin it before use."
    sha = revision.stdout.strip()
    # Avoid silently assessing a modified platform or inherited DSC.
    status = git(uefi, "status", "--porcelain", "--untracked-files=no", "--", *FILES)
    if status.returncode or status.stdout.strip():
        return False, "A relevant UEFI source file is modified or its status could not be read."
    result = git(uefi, "apply", "--check", str(PATCH))
    if result.returncode:
        return False, "Patch does not apply cleanly: " + result.stderr.strip()
    return True, f"Patch applies textually to {SUPPORTED[sha]} ({sha}); firmware is not built or verified."


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("uefi", type=Path, help="local UEFI Git checkout with garnet DSC/FDF present")
    args = parser.parse_args()
    try:
        ok, message = check(args.uefi)
    except OSError as error:
        ok, message = False, f"Could not execute Git: {error}"
    print(message, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
