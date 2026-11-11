#!/usr/bin/env python3
"""Apply the selected XNU patch series to a disposable clone, without building."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


DEVICE = Path(__file__).resolve().parents[1]
EXPECTED_XNU = "d8b80295118ef25ac3a784134bcf95cd8e88109f"


def run(args, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True, check=False, **kwargs)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")
    return result.stdout


def selected_inputs(status):
    sources = [module for module in status["modules"] if module["kind"] == "refer" and module["name"] == "xnu"]
    if len(sources) != 1 or not sources[0].get("path") or sources[0].get("pin") != EXPECTED_XNU:
        raise ValueError("Pinned XNU source is missing or does not match the research profile; run unixnu fetch xnu.")
    patches = [Path(value) for value in status["patch_order"]]
    if not patches or any(not path.is_file() for path in patches):
        raise ValueError("The selected XNU patch list is empty or references a missing file.")
    return Path(sources[0]["path"]), patches


def diagnostic_skip(patches, names):
    for name in names:
        if sum(patch.name == name for patch in patches) != 1:
            raise ValueError(f"Diagnostic skip must match exactly one selected patch: {name}")
    remaining = [patch for patch in patches if patch.name not in names]
    if not remaining:
        raise ValueError("Diagnostic skip omitted the entire patch series.")
    return remaining


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("unixnu", type=Path, help="local UniXNU checkout")
    parser.add_argument("--skip-name", action="append", default=[], metavar="PATCH",
                        help="diagnostic only: omit one named patch; never modifies board configuration")
    args = parser.parse_args()
    try:
        raw = run([sys.executable, str(args.unixnu / "unixnu"), "status", "--json", "-D", str(DEVICE)])
        source, patches = selected_inputs(json.loads(raw))
        patches = diagnostic_skip(patches, args.skip_name)
        actual = run(["git", "-C", str(source), "rev-parse", "HEAD"]).strip()
        if actual != EXPECTED_XNU:
            raise ValueError(f"XNU checkout HEAD is {actual}, expected {EXPECTED_XNU}")
        with tempfile.TemporaryDirectory(prefix="garnet-xnu-series-") as temp:
            work = Path(temp) / "xnu"
            run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(source), str(work)])
            run(["git", "-C", str(work), "checkout", "--quiet", "--detach", EXPECTED_XNU])
            for index, patch in enumerate(patches, 1):
                try:
                    run(["git", "-C", str(work), "apply", "--check", str(patch)])
                    run(["git", "-C", str(work), "apply", str(patch)])
                except RuntimeError as error:
                    raise RuntimeError(f"patch {index}/{len(patches)} {patch.name}: {error}") from error
        if args.skip_name:
            print("DIAGNOSTIC ONLY: skipped " + ", ".join(args.skip_name))
        print(f"PASS: {len(patches)} patches applied to XNU {EXPECTED_XNU} in a disposable clone.")
        print("Source preparation, compilation, ABI support and device boot were not tested.")
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError, RuntimeError) as error:
        print(f"XNU patch series check failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
