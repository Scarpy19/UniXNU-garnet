# UniXNU garnet port

Work-in-progress device port for the Xiaomi Redmi Note 13 Pro 5G / POCO X6 5G
(`garnet`, Qualcomm SM7435-AB). This repository does not yet contain a bootable
image or a verified device configuration.

## Status

- `board.example = true` — the configuration is guarded and cannot produce a boot image.
- OS profile is a research target (`ipados-27.0.1-24A446`), not an arm64e compatibility claim.
- No kernel, UEFI firmware, or boot image has been compiled.
- 72 XNU patches apply cleanly to a disposable clone of the pinned source.
- UEFI integration patch applies textually but has not been compiled or booted.

## Directory structure

```
UniXNU-garnet/
├── AGENTS.md              # AI agent handoff instructions
├── README.md              # This file
├── board.toml             # UniXNU device configuration (guarded)
├── feeds.toml             # Pinned SoC repository commit
├── porting.toml           # Porting record (13 areas, schema v1)
├── unixnu.lock            # Resolved XNU source commit
├── configs/
│   └── garnet_defconfig   # Kernel defconfig (minimal)
├── dts/
│   └── garnet.dts         # Device tree (minimal)
├── patches/
│   ├── uefi/
│   │   └── 0001-garnet-unixnu-handoff.patch
│   └── xnu/
│       ├── os27.series    # Provisional OS patch series
│       └── series         # Empty (placeholder)
├── scripts/
│   ├── check-uefi-patch.py
│   ├── check-xnu-series.py
│   └── inventory-uefi-inputs.py
├── tests/
│   ├── test_scaffold.py
│   ├── test_uefi_inventory.py
│   ├── test_uefi_patch_check.py
│   └── test_xnu_series_check.py
└── docs/
    ├── evidence.md         # Source inventory and claims
    ├── linux-host.md       # WSL/Linux build notes
    ├── uefi-integration.md # UEFI integration details
    └── verification.md     # Verification plan and results
```

## Prerequisites

- UniXNU checkout at `../UniXNU` (sibling directory)
- vildangil/UniXNU-sm7435-common at `../UniXNU-sm7435-common`
- WSL2 with Debian (or compatible Linux host)
- Python 3.11+
- Git

## Quick start

### 1. Validate configuration

```sh
cd ../UniXNU
python3 unixnu status --json -D ../UniXNU-garnet
```

### 2. Run tests

```sh
cd ../UniXNU-garnet
python3 -m unittest discover -s tests -v
```

### 3. Check porting record

```sh
cd ../UniXNU
python3 scripts/porting-record.py check --device ../UniXNU-garnet
```

### 4. Check UEFI patch

```sh
cd ../UniXNU-garnet
python3 scripts/check-uefi-patch.py ../uefi-garnet-reference
```

### 5. Check XNU patch series

```sh
cd ../UniXNU-garnet
python3 scripts/check-xnu-series.py ../UniXNU
```

## Hardware reference

| Component | Value |
|---|---|
| SoC | Qualcomm SM7435-AB (Snapdragon 7s Gen 2) |
| CPU | 4× Cortex-A78 @ 2.4 GHz + 4× Cortex-A55 @ 1.95 GHz |
| GPU | Adreno 710 Gen 7_3_0 (chip ID 0x07010000) |
| RAM | 8/12 GB LPDDR4X |
| Storage | UFS 2.2 |
| Display | AMOLED 1220×2712, 120 Hz |
| Touch | FocalTech FT3683G |
| UEFI FD | 0xA7100000, size 0x300000 |
| Kernel load | 0xA8000000 |
| XNU payload | 0xF4000000, size 0x04000000 |

## Key references

- UniXNU core: https://github.com/UniXNU/UniXNU
- SoC layer: https://github.com/vildangil/UniXNU-sm7435-common
- HakiOS reference: https://github.com/JosephMontfort/hakios-xnu-kernel-garnet
- Device HakiOS: https://github.com/JosephMontfort/hakios-sm7435
- UEFI upstream: https://github.com/Project-Silicium/Mu-Silicium

## Safety

- Do not flash or boot an image without explicit user approval.
- Keep firmware, blobs, device identifiers, and build artifacts out of this repository.
- Treat `fastboot boot` as a hardware operation requiring prior authorization.
- The `example = true` guard prevents accidental builds.

## License

This repository contains only original configuration and documentation.
Reference code is not included; see individual source repositories for their terms.