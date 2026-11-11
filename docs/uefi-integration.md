# Garnet UEFI integration

The candidate source is [garnet-linux/Mu-Silicium](https://github.com/garnet-linux/Mu-Silicium) at `f8779ea0bfb33e2aec31da4a902b4a4eb8abd044`. `patches/uefi/0001-garnet-unixnu-handoff.patch` is a **preliminary, unapplied source patch** against that revision, not a firmware image.

The patch adds the UniXNU menu, boot-option driver, initrd RAM-disk driver, and DarwinBoot to the platform DSC and FDF. It also declares DiskIo and FAT in the DSC and maps `HobLib` and `FdtLib`; the platform's existing `Include/DXE.inc` already places DiskIo, FAT, PartitionDxe, and English collation in the FDF.

The following only checks textual applicability against a checkout at the exact source revision:

```sh
git -C ../uefi-garnet-reference apply --check ../UniXNU-garnet/patches/uefi/0001-garnet-unixnu-handoff.patch
```

This check passed locally. It does not apply the patch, resolve library conflicts, check transitive package dependencies, build firmware, or establish that the FD fits or boots. Before building, review inherited DSC definitions, source licenses, submodules, vendor-input provenance and hashes, log exporter dependencies, `PACKAGES_PATH`, the target memory map, and firmware DTB. The current board guard remains enabled. Do not replace it with an existing prebuilt FD or assume boot-image header compatibility.

Use the [upstream firmware integration guide](https://unixnu.com/porting/uefi-firmware) and [log capture guide](https://unixnu.com/porting/log-capture). Hardware access, image boot and partition writes require the approvals described in `AGENTS.md`.
