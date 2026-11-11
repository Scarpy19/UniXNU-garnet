# Verification plan

The end goal is an evidence-backed boot on the user's garnet device, not merely a successful build. Record commands, source revisions, output hashes, failures, and test environment without publishing secrets or device identifiers.

1. **Source and licensing:** Verify repository revisions, licenses and component interfaces. Compare actual device inputs with SoC and upstream descriptions; do not copy assumptions from unrelated hardware.
2. **Configuration:** Populate the upstream device template only with supported, sourced values. Validate TOML and run UniXNU's porting-record checker, defconfig, status, and tree checks as applicable. A passing configuration check does not prove bootability.
3. **Host builds:** Establish a project-local toolchain and required external inputs. Compile the board DTS, kernel, UEFI and payload in stages; retain commands and hashes. Report missing dependencies and failed stages honestly. Check image structure and provenance independently.
4. **Hardware safety:** Before any device operation, explain the exact command, image provenance, recovery path and risks and obtain user approval. Never flash partitions without separate authorization. Confirm transport and log capture first.
5. **Hardware milestones:** Record UEFI output, loader handoff, XNU entry, SMP, storage, display, input, GPU, audio and battery separately. Distinguish device observations from upstream claims. Test on the relevant RAM variants before claiming both work.

No host build, device boot or peripheral success has been verified for this port yet.

## Initial scaffold checks

- `py -3.14 -m unittest discover -s tests -v`: checks the example guard, single-CPU intent, feed pin format, and device file references. This does not validate hardware.
- From the pinned UniXNU checkout, `py -3.14 scripts/porting-record.py check --device ../UniXNU-garnet` reports `garnet: 13 structured areas checked`. This checks the record schema, not whether the planned work is complete.
- The same checker with `--base bee69e8` also reports `13 structured areas checked` after adding ownership for the configuration and patch paths changed since that commit.
- `dtc -I dts -O dtb -i ../UniXNU-sm7435-common/dts -o /dev/null dts/garnet.dts`: syntax check only. The selected SoC DTSI reports `simple_bus_reg` for `/soc/timer`; investigate the binding before treating the description as complete. No DTB from this skeleton is suitable for boot.
- `python3 /mnt/d/UniXNU/UniXNU/unixnu build kernel -D /mnt/d/UniXNU/UniXNU-garnet`: on Debian WSL, UniXNU rejected the build with `EXAMPLE device repository` and exit code 1. Configuration loading fetched the pinned SoC feed before the guard ran, so this guard does not prevent all network or filesystem activity. The intentionally absent memory node and missing firmware configuration remain blockers.
