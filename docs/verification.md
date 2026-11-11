# Verification plan

The end goal is an evidence-backed boot on the user's garnet device, not merely a successful build. Record commands, source revisions, output hashes, failures, and test environment without publishing secrets or device identifiers.

1. **Source and licensing:** Verify repository revisions, licenses and component interfaces. Compare actual device inputs with SoC and upstream descriptions; do not copy assumptions from unrelated hardware.
2. **Configuration:** Populate the upstream device template only with supported, sourced values. Validate TOML and run UniXNU's porting-record checker, defconfig, status, and tree checks as applicable. A passing configuration check does not prove bootability.
3. **Host builds:** Establish a project-local toolchain and required external inputs. Compile the board DTS, kernel, UEFI and payload in stages; retain commands and hashes. Report missing dependencies and failed stages honestly. Check image structure and provenance independently.
4. **Hardware safety:** Before any device operation, explain the exact command, image provenance, recovery path and risks and obtain user approval. Never flash partitions without separate authorization. Confirm transport and log capture first.
5. **Hardware milestones:** Record UEFI output, loader handoff, XNU entry, SMP, storage, display, input, GPU, audio and battery separately. Distinguish device observations from upstream claims. Test on the relevant RAM variants before claiming both work.

Experimental kernel, UEFI, and payload host builds are recorded below. No boot image, device boot, or peripheral success has been verified.

## Initial scaffold checks

- `py -3.14 -m unittest discover -s tests -v`: checks the example guard, single-CPU intent, feed pin format, and device file references. This does not validate hardware.
- From the pinned UniXNU checkout, `py -3.14 scripts/porting-record.py check --device ../UniXNU-garnet` reports `garnet: 13 structured areas checked`. This checks the record schema, not whether the planned work is complete.
- The same checker with `--base bee69e8` also reports `13 structured areas checked` after adding ownership for the configuration and patch paths changed since that commit.
- `dtc -I dts -O dtb -i ../UniXNU-sm7435-common/dts -o /dev/null dts/garnet.dts`: syntax check only. The selected SoC DTSI reports `simple_bus_reg` for `/soc/timer`; investigate the binding before treating the description as complete. No DTB from this skeleton is suitable for boot.
- `python3 /mnt/d/UniXNU/UniXNU/unixnu build kernel -D /mnt/d/UniXNU/UniXNU-garnet`: on Debian WSL, UniXNU rejected the build with `EXAMPLE device repository` and exit code 1. Configuration loading fetched the pinned SoC feed before the guard ran, so this guard does not prevent all network or filesystem activity. The intentionally absent memory node and missing firmware configuration remain blockers.
- `git -C ../uefi-garnet-reference apply --check ../UniXNU-garnet/patches/uefi/0001-garnet-unixnu-handoff.patch`: passed against UEFI revision `f8779ea0bfb33e2aec31da4a902b4a4eb8abd044`. This is a patch applicability check, not a firmware build.
- `python3 scripts/check-uefi-patch.py ../uefi-garnet-reference`: reports that the patch applies textually to the pinned garnet-linux revision. The checker rejects unsupported revisions and dirty listed platform files; it does not validate a build.

## WSL configuration resolution

The following initial observations describe the previous iPadOS 27 profile, not the current iPadOS 17 target.

On the pinned UniXNU checkout, `python3 unixnu defconfig garnet_defconfig -D ../UniXNU-garnet` completed and generated an output configuration. `python3 unixnu status --json -D ../UniXNU-garnet` reported `configured: true`, the expected garnet device and pinned SM7435 feed, and the arm64e / iPadOS 27 research profile. It also reported an empty `kernel.archives` list and component catalog `os_abi` values for `ArmDTPlatform`, `ArmCpu`, and `SoftwareAES` listing the iPadOS 17 profile rather than the selected 27 profile. Inspection of `scripts/unixnu/kernel.py` shows that an empty list automatically expands selected component build recipes; it does not prove component archives are missing. Separately review whether auxiliary archive scripts and the selected ABI are supported before a real kernel build. Configuration resolution does not establish PAC support, successful patch application, ABI compatibility, firmware readiness or device boot.

The selected SM7435 SoC's `sm7435-smp-secondary.patch` does not apply to XNU `ac9718fb1af618d5ce8678d0dc6e8a58f252216f` after the corresponding architecture patch: its board configuration hunk expects four CPUs and one cluster, but the architecture patch defines eight CPUs and two clusters. A targeted two-file fixture and ordinary `git apply --check` failed on both patch hunks; the reset-vector hunk matches with `--unidiff-zero`, which the UniXNU patch workflow does not use. This is a partial source check, not a full series validation. The provisional board therefore omits the incompatible SoC patch series and retains `cpus=1`. Secondary CPU startup and eight-CPU support remain unimplemented and unverified for this profile.

`python3 scripts/check-xnu-series.py ../UniXNU` now checks the provisional series and reports `PASS: 72 patches applied to XNU ac9718fb1af618d5ce8678d0dc6e8a58f252216f in a disposable clone.` The initial check applied 69 patches and failed at `zzz-boot-progress.patch` on `bsd/kern/bsd_init.c`; that patch expects board-specific context absent from this port. The board now selects `patches/xnu/os27.series`, preserving the other three OS patches while omitting that incompatible boot-progress layer for initial research. No other patch in the pinned XNU patch directory refers to its symbols, but this static search does not prove all build dependencies are satisfied. The omitted layer includes boot diagnostics: provide and verify an alternative before attempting hardware bring-up. The board remains guarded; source patch applicability does not establish compilation or boot.

## Experimental build evidence (bringup/ios17)

On branch `bringup/ios17`, the selected profile is iPadOS 17 (`ipados-17.7.11-21H461`) and the resolved XNU source is `d8b80295118ef25ac3a784134bcf95cd8e88109f`. The XNU series check reports `PASS: 58 patches applied to XNU d8b80295118ef25ac3a784134bcf95cd8e88109f in a disposable clone`.

The native Linux XNU build completed and produced `kernel.macho` (51,015,680 bytes; SHA-256 `2c260065f0518ab20a1edd7b9361bbde5d117432581e562ddfe8da8fbacdc5e0`). Earlier bootstrap link errors for mockfs were reported, and the prelink step completed afterwards.

The garnet firmware build completed after adding the missing `UniXNULib` library assignment to the experimental board DSC, and rerunning with `ENABLE_SECUREBOOT=0`; the output firmware file is `SILICIUM_UEFI.fd` of 3,145,728 bytes.

The payload stage then succeeded after adding a single contiguous `memory@80000000` node to the experimental board DTS; it produced `payload.img` of 192 MiB. The boot image stage was then attempted against the experimental kernel and firmware and failed in the shim header validation with `unixnu: the ARM64 image header does not describe the shim plus the firmware volume`; no boot image was produced.

These artifacts are host-build outputs only. They do not prove device support, firmware safety, or a successful boot. The final boot image therefore remains to be produced; no boot image or device boot has been verified.

## iPadOS 17 WSL research branch

The native WSL checkout selects `ipados-17.7.11-21H461` and XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f`. `unixnu fetch`, `unixnu status --json`, and `unixnu defconfig garnet_defconfig` succeeded. `python3 scripts/check-xnu-series.py ../UniXNU` reported 58 patches applied in a disposable clone. The example guard remains enabled in the working branch. These checks alone do not validate the inherited iPad product identity and ADT data, compilation, iOS ABI, or hardware boot.

Using device commit `d242167` in a separate native WSL build clone with `example = false` only in that clone, `python3 unixnu build kernel -D ../UniXNU-garnet-build-ios17` completed and produced `out/garnet/ipados-17.7.11-21H461/garnet/kernel/kernel.macho` (51,015,680 bytes, SHA-256 `2c260065f0518ab20a1edd7b9361bbde5d117432581e562ddfe8da8fbacdc5e0`, independently checked with `sha256sum`). Its first bootstrap link reported missing mockfs symbols, after which the build created the supporting archives and completed the final prelink. This artifact includes Apple-derived prelinked inputs: do not publish it. Its successful build does not establish correct ADT, firmware compatibility, PAC behavior, iOS userspace compatibility, or hardware boot.

## Independent audit (2026-11-11)

The published WSL checkout was independently checked at `d95766f` on `bringup/ios17`; its working tree was clean and it tracked `origin/bringup/ios17`. `board.toml` still has `example = true`, and selects `ipados-17.7.11-21H461`. The source lock records XNU `d8b80295118ef25ac3a784134bcf95cd8e88109f` and SM7435 feed `cf8522069a9d54151bc42bfe487ac63b6a2c4aeb`. The series checker again passed with 58 patches, and the porting-record checker reported 13 structured areas.

The independently located host artifacts are:

* `kernel/kernel.macho`: 51,015,680 bytes, SHA-256 `2c260065f0518ab20a1edd7b9361bbde5d117432581e562ddfe8da8fbacdc5e0`.
* `payload/payload.img`: 201,326,592 bytes (192 MiB), SHA-256 `d03639e75aacf020732921195c492a9d250be6806cf105f2956b99f0f2030e6f`.
* `uefi-garnet-research/Build/garnetPkg/DEBUG_CLANGPDB/FV/SILICIUM_UEFI.fd`: 3,145,728 bytes, SHA-256 `5b2e8e440d1c22f789b8d577eb203c1843dedaaa22b2550ffe524161005199f3`; the firmware log ends with `- Done -`.

No `boot.img` was found under the WSL work area. Running `unixnu bootimg` with the experimental UEFI checkout and compiled hardware DTB failed in the BootShim validation with `the ARM64 image header does not describe the shim plus the firmware volume`. Therefore the host artifacts must not be described as a boot image or as device-ready. The memory node used to make the payload pass is a provisional `0x80000000` + `0x80000000` range and is not hardware evidence for garnet.

After correcting the experimental BootShim header to report the 112-byte shim plus the 3 MiB firmware volume, `unixnu bootimg` succeeded. The resulting untested artifact is `/home/scarpy/UniXNU/garnet-boot.img`, 202,551,296 bytes, SHA-256 `53dd4bbc40e62202ea39666a0fec947f622fb6619f1a635e080900673ab53fa8`. UniXNU's `boot.json` records a 192 MiB ramdisk, the firmware SHA-256 above, DTB SHA-256 `4568d0282ec04eef3ac9fca697850ab3a92eaa7c0aeadb70f579d681d96592bb`, 112-byte shim, and `hardware_tested: false`. The repository UEFI patch now includes both the UniXNU integration and the BootShim header correction; it was rechecked against a clean revision and applied textually.

This image is not device-verified. Its provisional memory map, inherited iPadOS identity, UEFI variables, firmware inputs, and kernel/DTB compatibility remain unverified. Do not boot or distribute it without a separate device-test review.

## Garnet device trial (2026-11-11)

The host copy was checked before testing: 202,551,296 bytes and SHA-256 `53dd4bbc40e62202ea39666a0fec947f622fb6619f1a635e080900673ab53fa8`. ADB identified the connected device as garnet / model `2312DRA50G`. The bootloader reported `product: garnet`, `unlocked: yes`, `secure: yes`, and `is-userspace: no` through read-only `fastboot getvar` queries.

The only image operation was `fastboot boot garnet-boot.img`; no `flash`, `erase`, or partition write was issued. Fastboot accepted and transferred the image (`Sending 'boot.img' ... OKAY`, `Booting OKAY`), but after 30 seconds the device remained in fastboot and did not expose ADB. This is a failed UEFI/XNU handoff, not a boot success. No UEFI or XNU logs were exposed over USB.

`fastboot reboot` returned `OKAY`. The device then appeared in recovery ADB, and `adb reboot` returned it to normal Android. Post-test Android properties reported `ro.product.device=garnet`, `ro.product.model=2312DRA50G`, and `MemTotal=7478208 kB` (consistent with an 8 GB variant). These observations do not establish the physical DRAM base or a contiguous memory range. Raw device logs are retained locally under `logs/device-test/` and are intentionally not committed because they contain device identifiers.

## HakiOS garnet DTB integration

The functional JosephMontfort HakiOS device repository is the primary garnet
reference for the second boot-image attempt. Its UEFI configuration confirms
`uefi_fd.base = 0xA7100000`, `uefi_fd.size = 0x300000`, and
`boot_shim.payload_base = 0xA8000000`. The UniXNU UEFI build already used the
same FD base and size; the important missing input was the functional garnet
DTB.

The HakiOS reference DTB was copied locally from
`hakios-sm7435/uefi/files/Resources/DTBs/garnet.dtb` to the WSL build output
as `build/garnet/hakios-garnet.dtb`. Its SHA-256 is
`66094d6eb28841efc765816b09b8db0d819502e04c7def57066278a4ae184848`.
It reports `ddr_size = <0x08>` and the same reserved-memory node names and
addresses observed through the live Android `/proc/device-tree` tree. It is a
reference input, not a read-back dump: SELinux blocked the live FDT properties
and the device bootloader does not support `fastboot fetch`.

The second image was built with that DTB and the existing iOS 17 kernel,
payload, and 3 MiB UEFI volume:

* `/home/scarpy/UniXNU/garnet-boot-hakios-dtb.img`
* 203,194,368 bytes
* SHA-256: `56c9fa7340a9170135f001e6c28d72db6834d294c4570d985219577027d8016e`

The boot-image board configuration now names the external DTB as
`build/garnet/hakios-garnet.dtb`. The simplified UniXNU DTS remains the ADT
source because the current ADT generator requires one contiguous memory range;
the HakiOS DTB preserves the real garnet multi-bank memory and reservations for
the Android boot-image handoff.

## Second garnet device trial

The second image was tested with the explicit user authorization to use
`fastboot boot` (RAM-only; no partition write):

* Image: `garnet-boot-hakios-dtb.img`
* Size: 203,194,368 bytes
* SHA-256: `56c9fa7340a9170135f001e6c28d72db6834d294c4570d985219577027d8016e`
* Fastboot transfer: `Sending 'boot.img' (198432 KB) OKAY`
* Boot request: `Booting OKAY`
* Total transfer time: 4.630 seconds

After 30 seconds, neither `fastboot devices` nor `adb devices` listed the
phone, which is expected while the firmware owns the display and USB loader.
The user observed the UniXNU menu on the garnet display. This confirms the
fastboot-to-UEFI handoff and a working UniXNU menu presentation. It does not
yet confirm XNU entry or peripheral operation. The test log is retained locally under
`logs/device-test/second-fastboot-boot.txt` and
`logs/device-test/second-post-30s.txt`; device identifiers are not committed.

## Repeat menu boot with complete host capture

The same image was booted again after the device was manually returned to
fastboot. The preflight hash and size matched the values above. Read-only
`fastboot getvar all` confirmed `product: garnet`, `kernel: uefi`,
`unlocked: yes`, `secure: yes`, `max-download-size: 0x30000000`, and
`current-slot: a`. The command output also contained the device serial number,
which is intentionally excluded from this record.

The second transfer completed as follows:

```text
Sending 'boot.img' (198432 KB) OKAY [ 4.289s ]
Booting OKAY [ 0.261s ]
Finished. Total time: 4.627s
```

The host captured USB state at 5, 15, 30, and 60 seconds. A fastboot transport
was briefly reported at 5 seconds and then disappeared; ADB never appeared.
The user observed the UniXNU menu on the display during this boot. Therefore
the display/menu checkpoint is confirmed again, while XNU entry and runtime
logs remain unconfirmed. Complete local logs are under
`logs/device-test/repeat-menu/` and are not committed because they contain
device identifiers.
