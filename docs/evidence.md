# Evidence inventory

## Scope and evidence levels

The target is `garnet`, Qualcomm SM7435-AB. A source statement is an upstream claim, not a confirmed result for this port. Hardware behavior requires a recorded test on the target. All listed revisions are observations, not yet selected build pins.

## Local references

| Project | Revision observed | Purpose |
| --- | --- | --- |
| [UniXNU](https://github.com/UniXNU/UniXNU) | `a74949b0d2fbfeb6936f9baee4e8e974c36c35fb` | Build driver and porting documentation. Its `AGENTS.md` points to `docs/`. |
| [UniXNU-sheng](https://github.com/UniXNU/UniXNU-sheng) | `0c865163139971264ea611fe4b4ab1e6c151b9e9` | Example format-2 device port; SM8550 settings are not garnet settings. |
| [hakios-sm7435](https://github.com/JosephMontfort/hakios-sm7435) | `ff80ac362505fca36600f084fd066f3e47028f93` | Garnet hardware and implementation reference. No root license was found; do not assume permission to copy its files. |
| [Android device tree](https://github.com/xiaomi-sm7435/android_device_xiaomi_garnet) | `5b7d0823c81ca7dcbbc8889615772e004957114a` | Android board configuration and hardware reference. |

## HakiOS repository layout

The [garnet HakiOS fork](https://github.com/JosephMontfort/hakios-xnu-kernel-garnet) uses `devices/manifest.conf` and `tools/hakios-device.py`, not `.gitmodules`, to compose device repositories. The garnet manifest points to `JosephMontfort/hakios-sm7435` at mutable `main`; resolve a commit before relying on it. Its device README claims working display, touch, SMP, OpenGL ES and UFS, partial audio and battery, and unfinished Metal, Wi-Fi and cellular. These are maintainer claims, not tests of this port.

The HakiOS common repository describes a mixture of APSL-2.0 and MIT licensing by directory; examine each file and its provenance. GitHub's lack of a detected license is not itself proof of a particular license. The separate `hakios-sm7435` repository has no root license identified in the investigation; treat its code and binaries as reference-only until rights are established.

## OS profile constraint

The [UniXNU arm64e guide](https://github.com/UniXNU/UniXNU/blob/a74949b0d2fbfeb6936f9baee4e8e974c36c35fb/docs/porting/arm64e.md) requires usable native pointer authentication on every enabled CPU for iOS/iPadOS 27 and lists only sheng as supported. Garnet support and EL1/EL0 behavior are not established. Do not claim that `--os 27` works. The guide identifies iPadOS 17 as an arm64 alternative, but choosing a fallback requires an explicit project decision.

## Device-tree and boot-image observations

The Android community [BoardConfig.mk](https://github.com/xiaomi-sm7435/android_device_xiaomi_garnet/blob/5b7d0823c81ca7dcbbc8889615772e004957114a/BoardConfig.mk) declares `parrot`, Android boot header version 4, a 4096-byte kernel page size, and prebuilt DTBs from a separate kernel repository. These are Android build configuration values, not independently verified bootloader requirements or permission to write partitions. Its architecture tuning string is a compiler configuration and is not proof of the physical CPU model.

UniXNU's [device-tree guide](https://github.com/UniXNU/UniXNU/blob/a74949b0d2fbfeb6936f9baee4e8e974c36c35fb/docs/porting/device-tree.md) distinguishes the board hardware tree used to generate the XNU ADT from the firmware DTB embedded in the boot image. They must not be treated as interchangeable. Confirm the exact DTB source and memory ranges for the actual device before generating either artifact.

## Host observations

The active GitHub CLI account was confirmed as `Scarpy19`. Debian on WSL2 is available and reports Python 3.13.5. The UniXNU Linux setup documentation says its normal installer writes toolchain content under `/opt` by default and shims under `/usr/bin`; it has not been run. The user requires work inside the project directory, so system-wide installation requires separate approval or a genuinely project-local solution.

## Open questions

- Verify exact SM7435 source revision, compatibility with the pinned UniXNU revision, and all SoC resource values against board evidence.
- Establish garnet RAM variants, reserved regions, DTB provenance, boot image geometry, firmware inputs and safe log transport.
- Verify native PAC requirements before selecting an arm64e profile.
- Establish licensing and provenance before reusing any reference implementation or publishing artifacts.
- Establish a reproducible toolchain contained in the project directory, or obtain approval for specific external changes.
