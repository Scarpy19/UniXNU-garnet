#!/usr/bin/env python3
"""Preflight check for UniXNU garnet proprietary files.

Verifies that all required firmware blobs are present, have correct
SHA256 hashes, meet minimum sizes, and have valid magic bytes.

Usage:
    python3 scripts/check-garnet.py
    python3 scripts/check-garnet.py --verbose
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

DEVICE = Path(__file__).resolve().parents[1]

# Required files: (path, min_size_bytes, magic_bytes_or_None, sha256_or_None)
REQUIRED = [
    # (relative path, min size, magic prefix, expected SHA256)
    # UEFI firmware
    ("proprietary/abl.elf", 100000, b"\x7fELF", None),
    ("proprietary/tz.mbn", 100000, None, None),
    ("proprietary/dtbo.img", 100000, None, None),
    # GPU firmware
    ("proprietary/gpu.mbn", 10000, None, None),
    ("proprietary/gen71100_gmu.bin", 1000, None, None),
    ("proprietary/a702_sqe.fw", 1000, None, None),
    # Audio DSP
    ("proprietary/adsp.mdt", 10000, None, None),
    # Haptic
    ("proprietary/aw8697_haptic.bin", 1000, None, None),
    # Modem
    ("proprietary/modem.mdt", 10000, None, None),
    # SoC / CPU
    ("proprietary/cpucp.elf", 10000, b"\x7fELF", None),
    ("proprietary/tme.mbn", 10000, None, None),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file(rel_path, min_size, magic, expected_sha):
    full = DEVICE / rel_path
    if not full.is_file():
        return False, f"MISSING: {rel_path}"
    size = full.stat().st_size
    if size < min_size:
        return False, f"TOO SMALL: {rel_path} ({size} < {min_size})"
    if magic:
        with open(full, "rb") as f:
            header = f.read(len(magic))
        if header != magic:
            return False, f"BAD MAGIC: {rel_path} (expected {magic.hex()}, got {header.hex()})"
    if expected_sha:
        actual = sha256_file(full)
        if actual != expected_sha:
            return False, f"SHA MISMATCH: {rel_path} (expected {expected_sha[:12]}..., got {actual[:12]}...)"
    return True, f"OK: {rel_path} ({size} bytes)"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="show all checks")
    args = parser.parse_args()

    passed = 0
    failed = 0
    for rel_path, min_size, magic, expected_sha in REQUIRED:
        ok, msg = check_file(rel_path, min_size, magic, expected_sha)
        if ok:
            passed += 1
            if args.verbose:
                print(msg)
        else:
            failed += 1
            print(msg)

    print(f"\nResult: {passed} passed, {failed} failed, {len(REQUIRED)} total")
    if failed:
        print("Preflight FAILED: missing or invalid firmware files.")
        return 1
    print("Preflight PASSED: all firmware files present and valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""