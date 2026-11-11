# UniXNU garnet port

This is a work-in-progress device port for the Xiaomi Redmi Note 13 Pro 5G / POCO X6 5G (`garnet`, Qualcomm SM7435-AB). It does not yet contain a bootable image or a verified device configuration. The format-2 configuration is guarded by `board.example = true`; its OS profile is a research target, not an arm64e compatibility claim. The DTS deliberately omits unverified RAM and board resources.

Start with [the AI handoff](AGENTS.md), [the porting record](porting.toml), [the evidence inventory](docs/evidence.md), and [the verification plan](docs/verification.md). Reference projects describe their own results; those results are not proof that this UniXNU port works.

Do not flash or boot an image without an explicit, device-specific safety review and user approval. Keep firmware, personal device data, unique identifiers, restore images, and build artifacts out of this public repository.
