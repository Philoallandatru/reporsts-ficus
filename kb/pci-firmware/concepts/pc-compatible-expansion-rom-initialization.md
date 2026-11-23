---
type: Concept
title: PC-Compatible Expansion ROM Initialization
description: PC-Compatible Expansion ROM Initialization is the POST/INIT contract
  for a PCI Expansion ROM image whose Code Type is 0, identifying Intel x86 PC-compatible
  code and an INIT ent...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PC-Compatible Expansion ROM Initialization

PC-Compatible Expansion ROM Initialization is the POST/INIT contract for a PCI Expansion ROM image whose Code Type is 0, identifying Intel x86 PC-compatible code and an INIT entry point at header offset `03h`. [PDF pp. 105-106](../_source/pages/page-105.md)

## Why it matters

The contract lets Revision 3.0-or-later ROM code initialize below 1 MiB and relocate its retained run-time portion to a firmware-selected final address, while preserving a legacy initialization path for older images. [PDF pp. 106-107](../_source/pages/page-106.md)

## Structure or behavior

The Code Type 0 header contains signature bytes `55h AAh`, Current Image Size at offset `02h` in 512-byte units, a three-byte INIT entry point at offset `03h`, application-reserved bytes through `17h`, and the PCI Data Structure pointer at offsets `18h`–`19h`. POST invokes INIT with a FAR CALL. [PDF p. 106](../_source/pages/page-106.md)

For a Revision 3.0-or-later image, POST places the image temporarily below 1 MiB, supplies Bus/Device/Function identity, the final run-time address in 16-byte units, and the segment:offset PMM Services Entry Point. INIT moves the final run-time image, and POST delays write protection until any Setup code has run before erasing the temporary copy. [PDF pp. 106-107](../_source/pages/page-106.md)

A legacy image is placed in the compatibility range, usually `0C 0000h` to `0E 0000h`; INIT receives only Bus/Device/Function identity. POST then write-protects the amount of RAM identified by Current Image Size. [PDF p. 107](../_source/pages/page-107.md)

INIT may reduce the retained run-time footprint by changing Current Image Size, or write zero to remove itself completely. If INIT changes the RAM image and retains a nonzero size, it must update the checksum so the byte-sum over the Current Image Size range is zero. [PDF pp. 107-108](../_source/pages/page-107.md)

Image Length is the complete ROM image and controls the initial image copy and ROM-chain layout. Initialization length and run-time length are both represented by Current Image Size at different lifecycle points; Image Length is not changed after INIT resizing. The PCI Data Structure must remain in the run-time portion when one exists, otherwise in the initialization portion. [PDF p. 108](../_source/pages/page-108.md)

Before INIT, firmware can reject an image whose Maximum Run-Time Image Length cannot fit the remaining placement space. Revision 3.0-or-later code accepts a fourth argument naming its final run-time address, so firmware may execute the larger initialization image at a separate below-1-MiB address and the ROM can move only its retained code to the final range. [PDF pp. 111-112](../_source/pages/page-111.md)

If the ROM enters Protected Mode, it must return to BIOS in Big Real Mode. A Revision 3.0-or-later image can coexist with Revision 2.1 firmware because the newer fields are ignored; when separate 2.1 and 3.x images exist for one device, the 2.1 image appears first but newer firmware prefers the 3.x image. [PDF pp. 111, 115](../_source/pages/page-111.md)

## Constraints and edge cases

The device must remain quiescent until its interrupt service routine is installed at the final run-time location, because an interrupt can arrive while interrupt chaining is being changed. POST must support a mixture of Revision 3.0-or-later and legacy ROMs. [PDF pp. 106-107](../_source/pages/page-106.md)

Before INIT, checksum validation covers the Current Image Size copied for initialization; after resizing, INIT is responsible for restoring a zero byte-sum over the new Current Image Size. [PDF p. 108](../_source/pages/page-108.md)

## Relationships

- [POST Expansion ROM Processing](post-expansion-rom-processing.md) selects and copies the image before this code-type-specific contract begins. [PDF pp. 104-105](../_source/pages/page-104.md)
- Revision 3 initialization receives the entry point for [POST Memory Manager Allocation](post-memory-manager-allocation.md). [PDF pp. 107, 109](../_source/pages/page-107.md)
- Image Length and Maximum Run-Time Image Length originate in the [PCI Data Structure](pci-data-structure.md). [PDF pp. 104, 108](../_source/pages/page-104.md)
- Final address, write protection, VGA treatment, and alignment are governed by [Expansion ROM Run-Time Placement](expansion-rom-runtime-placement.md). [PDF pp. 112-113](../_source/pages/page-112.md)

## Evidence

- [Code Type 0 header and Revision 3 POST extensions, PDF p. 106](../_source/pages/page-106.md)
- [INIT arguments, legacy path, and resizing, PDF p. 107](../_source/pages/page-107.md)
- [Checksum and three image lengths, PDF p. 108](../_source/pages/page-108.md)
- [Maximum run-time sizing and relocation admission, PDF pp. 111-112](../_source/pages/page-111.md)
- [Revision 2.1 compatibility and image ordering, PDF p. 115](../_source/pages/page-115.md)
