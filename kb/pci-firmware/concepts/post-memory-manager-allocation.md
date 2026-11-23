---
type: Concept
title: POST Memory Manager Allocation
description: POST Memory Manager (PMM) Allocation is the BIOS service model through
  which PCI Expansion ROM INIT code reserves temporary or permanent system memory
  instead of informally taki...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# POST Memory Manager Allocation

POST Memory Manager (PMM) Allocation is the BIOS service model through which PCI Expansion ROM INIT code reserves temporary or permanent system memory instead of informally taking EBDA or unused low-memory regions. [PDF p. 109](../_source/pages/page-109.md)

## Why it matters

It gives ROM initialization code a firmware-coordinated allocation mechanism and distinguishes scratch storage that expires at INIT return from storage that must remain reserved after the operating system boots. [PDF pp. 109-110](../_source/pages/page-109.md)

## Structure or behavior

Expansion ROM code calls PMM only during the INIT phase and requests either temporary or permanent memory. Before using `REQUEST_SYSTEM_MEMORY`, the ROM verifies that the system BIOS complies with version 3.0 or later. [PDF p. 109](../_source/pages/page-109.md)

Permanent memory remains assigned after operating-system boot. BIOS marks it reserved, private, and unmovable through Interrupt `15h`, function `E820h`, and must also describe the reserved region in ACPI memory tables. [PDF p. 110](../_source/pages/page-110.md)

Temporary memory is valid only while the ROM's initialization code is executing; after INIT returns to BIOS, its contents may be erased or overwritten. [PDF p. 110](../_source/pages/page-110.md)

An allocation request can select memory above or below the 1 MiB (`F FFFFh`) boundary. Below-1-MiB memory is scarce. Code retaining permanent memory above 1 MiB is expected to access it later while the operating system may run in protected mode. During INIT, BIOS calls the ROM in Big Real Mode with data access across the 32-bit memory range. [PDF p. 110](../_source/pages/page-110.md)

Across repeated calls, permanent allocations are limited in total to 64 KiB above 1 MiB and 40 KiB below 1 MiB. A ROM can query the currently available permanent maximum by calling PMM function 0 (`pmmAllocate`) with length zero and the applicable flags; every allocation result must be checked. [PDF p. 111](../_source/pages/page-111.md)

The PMM flags encode Memory Type in bits 1:0 (`1` conventional, `2` extended, `3` either), optional length-derived alignment in bit 2, and temporary versus permanent use in bit 3; bits 15:4 are reserved. [PDF p. 115](../_source/pages/page-115.md)

## Constraints and edge cases

ROM code must handle absent PMM support, absent permanent-memory support, and denied requests without failing unpredictably. Supporting a version 2.1 BIOS from a Revision 3.0-or-later ROM is a design choice, not a requirement. [PDF p. 109](../_source/pages/page-109.md)

The operating system must honor the firmware memory map; otherwise it can overwrite retained ROM memory. Both E820 and ACPI descriptions are required for permanent allocations. [PDF p. 110](../_source/pages/page-110.md)

The permanent limits apply to the sum of all requests by one ROM, while the firmware's available permanent pool is shared among multiple ROMs. Temporary and permanent requests may each be repeated, subject to those permanent totals. [PDF p. 111](../_source/pages/page-111.md)

## Relationships

- The PMM entry point is passed to Revision 3.0-or-later [PC-Compatible Expansion ROM Initialization](pc-compatible-expansion-rom-initialization.md). [PDF p. 107](../_source/pages/page-107.md)
- Permanent and temporary allocation limits and repeated-request rules continue in the following sections. [PDF pp. 110-111](../_source/pages/page-110.md)
- When PMM is unavailable, below-1-MiB allocation may fall back to carefully managed [Extended BIOS Data Area Usage](extended-bios-data-area.md). [PDF p. 114](../_source/pages/page-114.md)

## Evidence

- [PMM requirement, failure handling, and BIOS-version check, PDF p. 109](../_source/pages/page-109.md)
- [Permanent, temporary, and address-location semantics, PDF p. 110](../_source/pages/page-110.md)
- [Allocation totals, repeated calls, and protected-mode return state, PDF p. 111](../_source/pages/page-111.md)
- [PMM flag fields, PDF p. 115](../_source/pages/page-115.md)
