# Garnet Bring-Up Status

## Current checkpoint

The current iOS 17 experiment reaches the UniXNU UEFI application on a
garnet device through `fastboot boot`. The firmware receives the Android boot
image DTB and publishes the initrd as a read-only block device.

Observed on hardware:

```text
UNIXNURAMDISK: device tree at 0xAB34D000, 643457 bytes
UNIXNURAMDISK: initrd 0xAB54E000-0xB7FFEE8C rounded to 0xCAB1000 bytes
UNIXNURAMDISK: initrd block device 0xAB54E000 size 0xCAB1000 Success
Loading driver ... DarwinBoot.efi
Loading driver ... RamManagerDxe.efi
Successfully Mapped RAM Range: ...
```

This proves the SEC entry-argument HOB, DTB handoff, initrd discovery,
ramdisk Block I/O publication, and firmware-side DarwinBoot/RamManager
dispatch. It does not prove that DarwinBoot has loaded XNU.

## Current failure

UniXNU still falls back to its built-in action menu:

```text
UNIXNU: config: no boot entry found
UNIXNU: config: none found, using built-in configuration
UNIXNU: config: 4 entries, 0 drivers, 0 dt patches, 0 acpi tables, 0 slices, 0 kits loaded, 0 skipped
```

The payload is present and `mdir` sees these 8.3-compatible names:

```text
EFI/UniXNU/UNIXNU.TOM
EFI/UniXNU/Payloads/KERNEL
EFI/UniXNU/Payloads/KERNEL.ADT
```

The UEFI reader nevertheless returns `Unsupported` or `Not found` for every
enumerated `SimpleFileSystem` handle. The next diagnostic build enumerates the
root and `EFI` directory of every handle and calls `ConnectController` before
reading it. This is intended to identify whether the ramdisk handle is absent,
not connected, or mounted with unexpected contents.

## Experiments already ruled out

- Android boot image header v1 versus v4 did not change configuration lookup.
- Adding `linux,initrd-start/end` did not change configuration lookup.
- The HakiOS DTB and its garnet memory/reservation data are accepted.
- The SEC patch that preserves the entry argument and creates the
  `DAEE82E6-8090-4E72-BFB9-78C13CD4E359` HOB is present in the firmware; the
  hardware log proves that the HOB is consumed.
- Long-name payloads and generated FAT aliases were replaced with direct 8.3
  names; the reader still did not find the file.

## Hardware safety

All hardware tests used `fastboot boot`. No partition was flashed, erased, or
formatted. The device was returned to Android/recovery when needed. The host
does not receive UEFI logs through ADB or fastboot while the firmware menu is
active; the visible display output is currently the hardware log channel.

## Build inputs

- OS profile: `ipados-17.7.11-21H461`
- XNU revision: `d8b80295118ef25ac3a784134bcf95cd8e88109f`
- XNU patch series: 58 patches apply in a disposable clone
- Firmware base: `0xA7100000`, size `0x300000`
- Diagnostic payload size: 192 MiB
- First menu-reaching image: `garnet-boot-hakios-dtb.img`, SHA-256
  `56c9fa7340a9170135f001e6c28d72db6834d294c4570d985219577027d8016e`
- Volume-debug image: `garnet-boot-volume-debug.img`, SHA-256
  `ee1d60cf8e9130ab17eedab15510367de34dffbb937fcda035b86b5a2ace9b2a`

The images are local test artifacts and are not committed to this repository.
