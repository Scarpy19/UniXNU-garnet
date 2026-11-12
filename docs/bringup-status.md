# Garnet Bring-Up Status

## Current checkpoint

The iOS 17 experiment reaches the UniXNU UEFI application on a garnet device
through `fastboot boot`. The current firmware validates the initrd before
publishing it instead of trusting `/chosen` alone. The latest boot image
(Android boot header v0, explicit load addresses) was tested on hardware and
showed:

```text
=== UNIXNU RAMDISK SUMMARY ===
chosen  : 0xABFFF000-0xB7FFF000
payload : not found in memory
publish : not found
```

No payload FAT volume was published, so UniXNU still runs from its built-in
menu. XNU has not been entered.

## What this run proves

- The SEC entry-argument HOB (`DAEE82E6-8090-4E72-BFB9-78C13CD4E359`) and the
  Mu-Silicium DTB handoff work on garnet.
- `UniXNURamDiskDxe` is dispatched, read `/chosen` and printed the bootloader's
  own initrd range.
- The Android bootloader reports a 192 MiB initrd range whose end is exactly
  `0xB8000000`, the top of the "Kernel" window that garnet's `MemoryMapLib`
  declares at `0xA8000000` + `0x10000000`.
- The driver found no FAT boot sector (`0x55AA` signature plus the `UNIXNU`
  volume label) at the reported start, and its scan of conventional,
  boot-services and loader-data RAM found no payload elsewhere.

## What this run does not prove

- It does not prove that the bootloader copied the ramdisk bytes at all. An
  advertised `/chosen` range can be a reservation; the property is not evidence
  that the bytes are readable.
- It does not establish where the payload is, nor that another delivery path
  (smaller volume, in-firmware copy, storage partition) would succeed.
- It says nothing about DarwinBoot or XNU entry; the kernel prelink layout
  described below still blocks the loader.

## Boot image header experiment (v4 to v0)

The earlier images used Android boot header version 4, which carries no load
addresses. A UniXNU device record for marble, which uses the same Mu-Silicium
FDT handoff, states that "the earlier v4 image did not load the ramdisk
reliably" and that its working path is an Android v0 image with kernel
`0x80008000` and the payload at `0xA8000000`. That is a source claim from a
different board; it motivated the experiment, it did not establish garnet
behaviour.

The image was repacked with:

| field | value |
| --- | --- |
| `header_version` | 0 |
| `kernel_addr` | `0x80008000` |
| `ramdisk_addr` | `0xA8000000` |
| `tags_addr` | `0x81E00000` |
| `page_size` | 4096 |

`0x80000000` is the garnet DRAM base (`PcdSystemMemoryBase` in `garnet.dsc`);
`0xA8000000` is the start of the "Kernel" window in `MemoryMapLib`. The packed
header was re-read and verified before booting.

Result: the bootloader did not honour `ramdisk_addr`. It reported
`0xABFFF000-0xB7FFF000`, i.e. a 192 MiB ramdisk end-aligned to `0xB8000000`,
the top of the same window. The first sector at `0xABFFF000` was not a FAT
boot sector when the driver read it.

## Firmware changes used by this experiment

`UniXNURamDiskDxe` (UniXNU `package/UniXNUPkg/Driver/UniXNURamDiskDxe`) now:

- publishes `EFI_DISK_IO_PROTOCOL` next to Block I/O, because the EDK2 FAT
  driver requires Disk I/O on the controller handle;
- validates the start sector as the labelled payload FAT volume before
  publishing, instead of trusting `/chosen`;
- scans conventional, boot-services and loader-data RAM for that volume when
  `/chosen` does not validate;
- calls `ConnectController` and probes `EFI_SIMPLE_FILE_SYSTEM_PROTOCOL`;
- prints the summary block above and holds the console for 30 seconds.

These changes are local to the UniXNU checkout and are captured as patches in
`patches/diagnostics/`. The firmware still contains `DiskIoDxe`, `PartitionDxe`,
`Fat` and `EnglishDxe` through the stock `APRIORI.inc` / `DXE.inc` includes.

The payload volume is written with 8.3-compatible names only:

```text
EFI/UniXNU/UNIXNU.TOM
EFI/UniXNU/Payloads/KERNEL
EFI/UniXNU/Payloads/KERNEL.ADT
```

`UNIXNU.TOM` is 431 bytes; `KERNEL` is 51,015,680 bytes; `KERNEL.ADT` is
13,652 bytes. `mdir` reads all three from the built `payload.img`.

## Experiments already ruled out

- Android boot header v1 and v4: the bootloader either did not load the payload
  or placed it where the firmware could not find it. v0 shows that a range is
  advertised, but no FAT volume is readable there.
- Writing guessed `linux,initrd-start/end` values into the firmware DTB
  (`0xA8000000-0xB4000000`): removed. The values above are the bootloader's own.
- Long VFAT names and generated 8.3 aliases: replaced by direct 8.3 names. The
  reader no longer fails on names, but the volume is still absent.
- Missing `UniXNULib` in the board DSC and the SEC entry-argument patch: both
  are fixed and required; the HOB is consumed on hardware.
- The HakiOS garnet DTB and its memory reservations are accepted by the
  firmware.

## Open questions

1. Does ABL copy the ramdisk bytes for `fastboot boot`, or only reserve the
   advertised range? A read-back of `0xABFFF000` (FAT signature, or a hex dump
   UEFI application) answers this without changing the delivery path.
2. If the bytes are absent, does a smaller payload (64 or 96 MiB) change
   anything? The range would still end at `0xB8000000`, so size is unlikely to
   be the cause.
3. Which alternative delivery should be tested next: a payload copied by
   BootShim to a fixed address, a payload embedded in the firmware volume, or a
   storage partition? None of these has been implemented.
4. Independent of discovery, `HakiOS/xnuloader` rejects the kernel with
   `unexpected kernel layout`: `__TEXT` is at `0xfffffff007004000` while
   `__PRELINK_TEXT` starts at `0xfffffff00427c000`, below
   `KERNEL_VIRT_BASE + KERNEL_LINK_OFFSET` (`0xfffffff007000000`). The prelink
   address in `scripts/build-xnu-4k-baseline.sh` still has to be corrected.

## Hardware safety

All hardware tests used `fastboot boot`. No partition was flashed, erased or
formatted. The host does not receive UEFI logs over USB while the firmware owns
the display; the visible console is the only log channel. Local logs under
`logs/device-test/` are not committed because they contain device identifiers.

## Build inputs

- OS profile: `ipados-17.7.11-21H461`
- XNU revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`
- XNU patch series: 58 patches apply in a disposable clone
- Firmware base: `0xA7100000`, size `0x300000`
- Firmware defines: `ENABLE_SECUREBOOT=0`,
  `UNIXNU_GARNET_FALLBACK_INITRD_BASE=0xA8000000`,
  `UNIXNU_GARNET_FALLBACK_INITRD_SIZE=0x0C000000`
- Firmware volume: `SILICIUM_UEFI.fd`, 3,145,728 bytes, SHA-256
  `92f85c8bd073953f731956c1327f0230374868081af1eaa9483f92aeb76b8114`
- Payload: 201,326,592 bytes (192 MiB FAT32, label `UNIXNU`), SHA-256
  `90925bde34cec351bc315a4b85743ccf5cf6a8006ab4682673a7b9257ee65476`
- Boot DTB: `hakios-garnet.dtb`, SHA-256
  `66094d6eb28841efc765816b09b8db0d819502e04c7def57066278a4ae184848`
- Latest boot image: `garnet-boot-v0.img`, 203,194,368 bytes, header v0,
  kernel `0x80008000`, ramdisk `0xA8000000`, tags `0x81E00000`, page size 4096,
  SHA-256 `d6e5d7f039cc42cc3ad4e11522de54e230cbc25334c85069830f5a92929cf9e0`

The images are local test artifacts and are not committed to this repository.
