# Garnet UEFI integration

The candidate source is [garnet-linux/Mu-Silicium](https://github.com/garnet-linux/Mu-Silicium) at `f8779ea0bfb33e2aec31da4a902b4a4eb8abd044`. `patches/uefi/0001-garnet-unixnu-handoff.patch` is a **preliminary, unapplied source patch** against that revision, not a firmware image.

The patch adds the UniXNU menu, boot-option driver, initrd RAM-disk driver, and DarwinBoot to the platform DSC and FDF. It also declares DiskIo and FAT in the DSC and maps `HobLib` and `FdtLib`; the platform's existing `Include/DXE.inc` already places DiskIo, FAT, PartitionDxe, and English collation in the FDF.

The following only checks textual applicability against a checkout at the exact source revision:

```sh
git -C ../uefi-garnet-reference apply --check ../UniXNU-garnet/patches/uefi/0001-garnet-unixnu-handoff.patch
```

This check passed locally. It does not apply the patch, resolve library conflicts, check transitive package dependencies, build firmware, or establish that the FD fits or boots. Before building, review inherited DSC definitions, source licenses, submodules, vendor-input provenance and hashes, log exporter dependencies, `PACKAGES_PATH`, the target memory map, and firmware DTB. The current board guard remains enabled. Do not replace it with an existing prebuilt FD or assume boot-image header compatibility.

## Persistent boot-variable risk

The proposed patch includes `UniXNUDxe`. In the pinned UniXNU source, `package/UniXNUPkg/Driver/UniXNUDxe/UniXNUDxe.c` uses `SetVariable` with `EFI_VARIABLE_NON_VOLATILE` to register a `Boot####` option and place it first in `BootOrder`. Therefore, even a temporary `fastboot boot` of firmware containing this driver could modify persistent UEFI variables if the platform provides persistent variable services. Whether garnet's implementation does so and how to restore it have not been established. Do not boot this patch until its variable behavior, a non-persistent alternative or explicit rollback, and device recovery have been reviewed and the user separately approves the exact test.

## Vendor-input reference inventory

`python3 scripts/inventory-uefi-inputs.py ../uefi-garnet-reference` reads the pinned Git revision and lists garnet-specific binary INF and RAW references from `Include/DXE.inc` and `Include/RAW.inc`. It includes entries inside conditional blocks without evaluating the conditions. It does not read binaries or prove which references are needed by a build, whether files exist, whether INF transitive dependencies exist, or whether redistribution is permitted. Use it as a starting point for a provenance and hash inventory, not as an extraction or flashing script.

At the pinned revision this reported **51 INF references and 6 RAW references**, including conditional entries. `git ls-tree -r --name-only HEAD Binaries/garnet` in the reference checkout returned no tracked files at that path. This does not establish whether a separately obtained vendor input is available or usable.

Use the [upstream firmware integration guide](https://unixnu.com/porting/uefi-firmware) and [log capture guide](https://unixnu.com/porting/log-capture). Hardware access, image boot and partition writes require the approvals described in `AGENTS.md`.
