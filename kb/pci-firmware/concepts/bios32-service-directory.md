---
type: Concept
title: BIOS32 Service Directory
description: The BIOS32 Service Directory is a discovery and dispatch mechanism for
  32-bit BIOS services, including the PCI BIOS. Its presence is advertised by a contiguous,
  checksummed 16-b...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# BIOS32 Service Directory

The BIOS32 Service Directory is a discovery and dispatch mechanism for 32-bit BIOS services, including the PCI BIOS. Its presence is advertised by a contiguous, checksummed 16-byte structure aligned on a 16-byte boundary in physical address range `0E0000h` through `0FFFFFh`. [PDF pp. 11-12](../_source/pages/page-011.md)

## Structure or behavior

The structure starts with ASCII signature `_32_`, contains a physical entry-point address, revision, paragraph-unit length, checksum, and reserved bytes. Clients scan through `0FFFF0h`, validate both signature and checksum, then invoke the directory with `CALL FAR`. [PDF p. 12](../_source/pages/page-012.md)

The directory accepts a four-character service identifier and returns a service base address, length, and entry-point offset when present. The PCI BIOS service identifier is `$PCI` (`49435024h`). [PDF p. 13](../_source/pages/page-013.md)

## Constraints and edge cases

The calling environment must map the entry page and following page in matching-base CS and DS selectors, provide at least 1 KiB of stack, and permit I/O-space access. [PDF pp. 12-13](../_source/pages/page-012.md)

## Evidence

- [Discovery range and structure introduction, PDF p. 11](../_source/pages/page-011.md)
- [Structure fields and calling environment, PDF p. 12](../_source/pages/page-012.md)
- [Return contract and `$PCI` identifier, PDF p. 13](../_source/pages/page-013.md)
