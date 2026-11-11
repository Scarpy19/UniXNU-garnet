# Verification plan

The end goal is an evidence-backed boot on the user's garnet device, not merely a successful build. Record commands, source revisions, output hashes, failures, and test environment without publishing secrets or device identifiers.

1. **Source and licensing:** Verify repository revisions, licenses and component interfaces. Compare actual device inputs with SoC and upstream descriptions; do not copy assumptions from unrelated hardware.
2. **Configuration:** Populate the upstream device template only with supported, sourced values. Validate TOML and run UniXNU's porting-record checker, defconfig, status, and tree checks as applicable. A passing configuration check does not prove bootability.
3. **Host builds:** Establish a project-local toolchain and required external inputs. Compile the board DTS, kernel, UEFI and payload in stages; retain commands and hashes. Report missing dependencies and failed stages honestly. Check image structure and provenance independently.
4. **Hardware safety:** Before any device operation, explain the exact command, image provenance, recovery path and risks and obtain user approval. Never flash partitions without separate authorization. Confirm transport and log capture first.
5. **Hardware milestones:** Record UEFI output, loader handoff, XNU entry, SMP, storage, display, input, GPU, audio and battery separately. Distinguish device observations from upstream claims. Test on the relevant RAM variants before claiming both work.

An experimental kernel host build is recorded below. No garnet UEFI build, device boot or peripheral success has been verified.

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
