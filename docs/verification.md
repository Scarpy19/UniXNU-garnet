# Verification plan

The end goal is an evidence-backed boot on the user's garnet device, not merely a successful build. Record commands, source revisions, output hashes, failures, and test environment without publishing secrets or device identifiers.

1. **Source and licensing:** Verify repository revisions, licenses and component interfaces. Compare actual device inputs with SoC and upstream descriptions; do not copy unrelated SM8550 assumptions.
2. **Configuration:** Populate the upstream device template only with supported, sourced values. Validate TOML and run UniXNU's porting-record checker, defconfig, status, and tree checks as applicable. A passing configuration check does not prove bootability.
3. **Host builds:** Establish a project-local toolchain and required external inputs. Compile the board DTS, kernel, UEFI and payload in stages; retain commands and hashes. Report missing dependencies and failed stages honestly. Check image structure and provenance independently.
4. **Hardware safety:** Before any device operation, explain the exact command, image provenance, recovery path and risks and obtain user approval. Never flash partitions without separate authorization. Confirm transport and log capture first.
5. **Hardware milestones:** Record UEFI output, loader handoff, XNU entry, SMP, storage, display, input, GPU, audio and battery separately. Distinguish device observations from upstream claims. Test on the relevant RAM variants before claiming both work.

No host build, device boot or peripheral success has been verified for this port yet.
