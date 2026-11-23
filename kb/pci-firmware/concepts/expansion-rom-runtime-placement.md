---
type: Concept
title: Expansion ROM Run-Time Placement
description: Expansion ROM Run-Time Placement is the Revision 3.0-or-later firmware
  contract for choosing, protecting, and aligning the final below-1-MiB address of
  retained PC-compatible RO...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Expansion ROM Run-Time Placement

Expansion ROM Run-Time Placement is the Revision 3.0-or-later firmware contract for choosing, protecting, and aligning the final below-1-MiB address of retained PC-compatible ROM code. [PDF pp. 112-113](../_source/pages/page-112.md)

## Why it matters

Separating the temporary INIT range from the final run-time range lets a large initialization image execute even when only its smaller retained portion fits the compatibility area. [PDF p. 112](../_source/pages/page-112.md)

## Structure or behavior

The fourth INIT argument supplies the final run-time address. Temporary and final ranges may be identical or entirely separate, but must not partially overlap; the ROM moves retained code and makes installed interrupt vectors point to its final location before returning. [PDF p. 112](../_source/pages/page-112.md)

Revision 3.0-or-later firmware may place a matching ROM at an aligned address from `A 0000h` through `F FFFFh`; older images remain in the legacy `0C 0000h` through `0E 0000h` range. Firmware must write-protect the final run-time region. [PDF pp. 112-113](../_source/pages/page-112.md)

A Revision 3.0-or-later VGA ROM need not occupy `0C 0000h`; firmware identifies VGA ownership from the PCI Data Structure Class Code rather than placement. Newer images may use 512-byte alignment, while firmware must account for legacy software that scans only 2-KiB boundaries. [PDF p. 113](../_source/pages/page-113.md)

## Constraints and edge cases

The `A 0000h`–`B FFFFh` range is the legacy VGA frame buffer and should be excluded while VGA is supported. A platform also cannot use a candidate region if it cannot provide required write protection. [PDF p. 113](../_source/pages/page-113.md)

## Relationships

- [PC-Compatible Expansion ROM Initialization](pc-compatible-expansion-rom-initialization.md) consumes the final address and relocates retained code. [PDF p. 112](../_source/pages/page-112.md)
- Revision 3.0-or-later ROMs must support the BIOS Boot Specification, but PCI Firmware 3.3 supersedes it for placement range, VGA placement, and alignment. [PDF p. 113](../_source/pages/page-113.md)

## Evidence

- [Relocation and placement range, PDF p. 112](../_source/pages/page-112.md)
- [Protection, VGA placement, and alignment, PDF p. 113](../_source/pages/page-113.md)
