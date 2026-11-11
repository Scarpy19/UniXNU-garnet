# Evidence inventory

## Scope and evidence levels

The target is `garnet`, Qualcomm SM7435-AB. A source statement is an upstream claim, not a confirmed result for this port. Hardware behavior requires a recorded test on the target. All listed revisions are observations, not yet selected build pins.

## Local references

| Project | Revision observed | Purpose |
| --- | --- | --- |
| [UniXNU](https://github.com/UniXNU/UniXNU) | `a74949b0d2fbfeb6936f9baee4e8e974c36c35fb` | Build driver and porting documentation. Its `AGENTS.md` points to `docs/`. |
| [UniXNU-sm7435-common](https://github.com/vildangil/UniXNU-sm7435-common) | `cf8522069a9d54151bc42bfe487ac63b6a2c4aeb` | Preliminary SM7435 source reference selected in `feeds.toml`; not verified on garnet. |
| [hakios-sm7435](https://github.com/JosephMontfort/hakios-sm7435) | `ff80ac362505fca36600f084fd066f3e47028f93` | Garnet hardware and implementation reference. No root license was found; do not assume permission to copy its files. |
| [Android device tree](https://github.com/xiaomi-sm7435/android_device_xiaomi_garnet) | `5b7d0823c81ca7dcbbc8889615772e004957114a` | Android board configuration and hardware reference. |

## HakiOS repository layout

The [garnet HakiOS fork](https://github.com/JosephMontfort/hakios-xnu-kernel-garnet) uses `devices/manifest.conf` and `tools/hakios-device.py`, not `.gitmodules`, to compose device repositories. The garnet manifest points to `JosephMontfort/hakios-sm7435` at mutable `main`; resolve a commit before relying on it. Its device README claims working display, touch, SMP, OpenGL ES and UFS, partial audio and battery, and unfinished Metal, Wi-Fi and cellular. These are maintainer claims, not tests of this port.

The project user states that JosephMontfort's HakiOS boots successfully on garnet. Treat that as user-reported reference evidence and prioritize the reference boot chain and hardware configuration. It is not an observation of this UniXNU build or proof that the same driver, firmware or OS ABI can be used unchanged.

At the recorded `hakios-sm7435` revision, `uefi/files/Resources/Configs/garnet.toml` specifies an Android boot image header version of 4, a gzip-compressed kernel field with appended DTB, and UEFI FD base `0xa7100000` and size `0x300000`. `garnet-boot.sh` describes a separate resident-loader workflow that pushes a system ramdisk and boots HakiOS with its own arguments. Those facts explain the reference workflow, not compatibility with UniXNU's payload or proof that its image settings can be transferred unchanged. The reference's `pull-firmware.sh` also requests modem and other firmware; it has not been run and is outside the scope of the approved read-only model/CPU queries.

The HakiOS common repository describes a mixture of APSL-2.0 and MIT licensing by directory; examine each file and its provenance. GitHub's lack of a detected license is not itself proof of a particular license. The separate `hakios-sm7435` repository has no root license identified in the investigation; treat its code and binaries as reference-only until rights are established.

## OS profile constraint

The [UniXNU arm64e guide](https://github.com/UniXNU/UniXNU/blob/a74949b0d2fbfeb6936f9baee4e8e974c36c35fb/docs/porting/arm64e.md) requires usable native pointer authentication on every enabled CPU for iOS/iPadOS 27 and does not list garnet as supported. Garnet support and EL1/EL0 behavior are not established. Do not claim that `--os 27` works. The guide identifies iPadOS 17 as an arm64 alternative, but choosing a fallback requires an explicit project decision.

The preliminary `board.toml` names the requested 27 profile solely to structure the investigation. It remains marked as an example and must not be used to build or boot a device image until PAC, memory, firmware and the remaining inputs are verified. The SoC source describes its SMP patch as experimental and recommends single-CPU bring-up; `cpus=1` is a conservative target, not a validated boot configuration.

With the user's permission, read-only ADB queries on the connected target running a custom Android ROM reported eight processors. The `/proc/cpuinfo` feature list did not advertise `paca` or `pacg`. These are observations from the running Android kernel, not a conclusive test of architectural PAC availability, per-core key access, or the UEFI/XNU execution environment. No device serial or user data was recorded.

## Device-tree and boot-image observations

The Android community [BoardConfig.mk](https://github.com/xiaomi-sm7435/android_device_xiaomi_garnet/blob/5b7d0823c81ca7dcbbc8889615772e004957114a/BoardConfig.mk) declares `parrot`, Android boot header version 4, a 4096-byte kernel page size, and prebuilt DTBs from a separate kernel repository. These are Android build configuration values, not independently verified bootloader requirements or permission to write partitions. Its architecture tuning string is a compiler configuration and is not proof of the physical CPU model.

UniXNU's [device-tree guide](https://github.com/UniXNU/UniXNU/blob/a74949b0d2fbfeb6936f9baee4e8e974c36c35fb/docs/porting/device-tree.md) distinguishes the board hardware tree used to generate the XNU ADT from the firmware DTB embedded in the boot image. They must not be treated as interchangeable. Confirm the exact DTB source and memory ranges for the actual device before generating either artifact.

The HakiOS reference at commit `ff80ac362505fca36600f084fd066f3e47028f93` includes `prebuilt/device-tree.dtb`, SHA-256 `66094d6eb28841efc765816b09b8db0d819502e04c7def57066278a4ae184848`. Its root model names garnet and its compatible strings include `qcom,parrot-qrd` and `qcom,parrot`. Debian `dtc -I dtb -O dts -o /dev/null` returned successfully but reported numerous binding and `reg` warnings. `fdtget` showed multiple `/memory` entries including zero-size values. A root-child listing returned exit code 1 after partial output. These observations concern an unlicensed, externally supplied prebuilt, not the connected device's live tree. They do not establish a safe boot DTB or usable RAM map; do not redistribute or use it without provenance, binding and target validation.

## UEFI integration evidence

[Project-Silicium PR 2166](https://github.com/Project-Silicium/Mu-Silicium/pull/2166) was merged as `7a2ada19841a129f86fb791c0b9a710436c849a4`; it changes garnet memory-map entries to address a reported Linux boot exception. This is not evidence of an XNU boot. The public [garnet fork](https://github.com/garnet-linux/Mu-Silicium/tree/f8779ea0bfb33e2aec31da4a902b4a4eb8abd044) has a later revision with a different memory map, so the precise revision matters.

[JosephMontfort/Mu-Silicium](https://github.com/JosephMontfort/Mu-Silicium/tree/425ed9ad8c78f8cee48886be1f9ed1e74d4e0b55) is another public firmware reference. Its observed commit `425ed9ad8c78f8cee48886be1f9ed1e74d4e0b55` adds hardware reservation entries to garnet's memory-map source compared with the pinned garnet-linux reference. The differences need independent review against the intended boot chain and device; they have not been transferred to this port. The source review did not identify a DarwinBoot integration in that revision.

That fork's `Resources/Configs/garnet.toml` specifies boot header version 4, while the garnet-linux candidate specifies version 1. The HakiOS device repository's own UEFI overlay is not identical to either baseline: its memory map marks the kernel region differently and adds an XNU payload reservation. In particular, the separately pinned JosephMontfort Mu-Silicium baseline does not itself contain that HakiOS overlay's XNU payload reservation. These are source-level comparisons, not a validated memory layout for UniXNU; do not mix an overlay, boot shim, payload or DTB from different revisions without tracing their handoff and allocation rules.

At that fork revision, the garnet configuration describes a boot image using header version 1, whereas the Android community board configuration specifies version 4. These refer to different build paths; do not assume either is valid for our planned image without examining the selected boot chain and testing safely. The fork's garnet DSC/FDF was reported to lack UniXNU and DarwinBoot modules. Integration, source and licensing review, compilation, and on-device validation are still required. Do not redistribute vendor binaries merely because a public source tree references them.

## Android kernel and vendor references

The [Android kernel reference](https://github.com/xiaomi-sm7435/android_device_xiaomi_garnet-kernel/tree/6e6db68f9db4252299d3a14da13c4eba340b1a3c) contains prebuilt kernel, DTBO and multiple DTBs; selecting one for a particular device requires independent identification and provenance checks. The [vendor reference](https://github.com/xiaomi-sm7435/android_vendor_xiaomi_garnet/tree/ade07bb99a448a3d077435ecef3760c31bf402c8) publicly contains proprietary firmware and other binary files. Thus it would be incorrect to state that no proprietary blobs are publicly accessible. Neither repository's investigated tree provided clear redistribution terms; do not copy or publish its binaries without establishing the applicable rights. Public availability does not establish authenticity, compatibility, or a license.

## Host observations

The active GitHub CLI account was confirmed as `Scarpy19`. Debian on WSL2 is available and reports Python 3.13.5. The UniXNU Linux setup documentation says its normal installer writes toolchain content under `/opt` by default and shims under `/usr/bin`; it has not been run. The user requires work inside the project directory, so system-wide installation requires separate approval or a genuinely project-local solution.

## Open questions

- Verify exact SM7435 source revision, compatibility with the pinned UniXNU revision, and all SoC resource values against board evidence.
- Establish garnet RAM variants, reserved regions, DTB provenance, boot image geometry, firmware inputs and safe log transport.
- Verify native PAC requirements before selecting an arm64e profile.
- Establish licensing and provenance before reusing any reference implementation or publishing artifacts.
- Establish a reproducible toolchain contained in the project directory, or obtain approval for specific external changes.
