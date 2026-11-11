# Agent handoff

Read this file, `README.md`, `docs/evidence.md`, and `docs/verification.md` before working. Read `../UniXNU/AGENTS.md` and the relevant UniXNU porting documentation before modifying the device configuration. Reference repositories are siblings under the project workspace, not part of this repository.

## Rules

- Document findings, source revisions, commands, limitations, and failures in English. Separate source claims from independently verified results.
- Keep this repository and future repositories for this port focused on garnet; do not include unrelated device support or documentation.
- Never guess hardware addresses, memory reservations, firmware inputs, ABI compatibility, or device support. Confirm values from the actual board and independent sources.
- Follow the upstream format-2 device repository and porting-record requirements. Keep the port explicitly incomplete until its inputs and validation are complete.
- Do not copy code or distribute binaries from a repository without checking the license and file provenance. A public repository is not by itself a redistribution license.
- Do not commit firmware, vendor blobs, device identifiers, credentials, restore images, or personal data. Review every change before publishing it.
- Do not install software outside the project workspace, change host system paths, or access the phone without the user's explicit approval.
- Treat `fastboot boot` as a hardware operation requiring prior user approval; do not flash partitions without separate explicit authorization.
- Keep UniXNU, SoC, firmware, and device revisions pinned and record the provenance of every borrowed fact or implementation.
- Perform all compilation from synchronized checkouts in the native WSL filesystem under `/home/scarpy/UniXNU`; preserve uncommitted changes when synchronizing.
