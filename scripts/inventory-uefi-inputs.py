#!/usr/bin/env python3
"""List garnet binary references from the pinned UEFI source, without blobs."""

import argparse
from pathlib import Path
import re
import subprocess
import sys


REVISION = "f8779ea0bfb33e2aec31da4a902b4a4eb8abd044"
DXE_SOURCE = "Platforms/Xiaomi/garnetPkg/Include/DXE.inc"
RAW_SOURCE = "Platforms/Xiaomi/garnetPkg/Include/RAW.inc"
INF = re.compile(r"^\s*INF\s+(Binaries/garnet/[^\s#]+\.inf)\s*(?:#.*)?$", re.IGNORECASE)
RAW = re.compile(r"^\s*SECTION\s+RAW\s*=\s*(Binaries/garnet/[^\s#]+)\s*(?:#.*)?$", re.IGNORECASE)


def referenced_infs(text):
    """Return sorted unique references, including those in conditional blocks."""
    return sorted({match.group(1) for line in text.splitlines() if (match := INF.match(line))})


def referenced_raw_files(text):
    """Return sorted unique RAW references, including conditional entries."""
    return sorted({match.group(1) for line in text.splitlines() if (match := RAW.match(line))})


def read_source(uefi, source):
    result = subprocess.run(
        ["git", "-C", str(uefi), "show", f"{REVISION}:{source}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("uefi", type=Path, help="local Mu-Silicium reference Git checkout")
    args = parser.parse_args()
    try:
        infs = referenced_infs(read_source(args.uefi, DXE_SOURCE))
        raw = referenced_raw_files(read_source(args.uefi, RAW_SOURCE))
    except (OSError, RuntimeError) as error:
        print(f"Unable to read the pinned UEFI source: {error}", file=sys.stderr)
        return 1
    if not infs or not raw:
        print("Expected binary references not found; inspect the sources manually.", file=sys.stderr)
        return 1
    print(f"Source revision: {REVISION}")
    print(f"Binary INF references: {len(infs)}; RAW references: {len(raw)} (includes conditional entries)")
    print("References only: this does not check file existence, hashes, license, or build selection.")
    print("\n".join(infs + raw))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
