---
type: Concept
title: PCI BIOS Present
description: PCI BIOS Present is the Traditional PCI BIOS capability-discovery call.
  It validates that the PCI BIOS function set exists and reports its interface version,
  configuration-acces...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI BIOS Present

PCI BIOS Present is the Traditional PCI BIOS capability-discovery call. It validates that the PCI BIOS function set exists and reports its interface version, configuration-access mechanisms, Special Cycle support, last bus number, and—starting with interface version 3.0—implemented function groups. [PDF pp. 14-15](../_source/pages/page-014.md)

## Structure or behavior

Presence is valid only when Carry Flag is clear, `AH` is `00h`, and `EDX` contains `PCI` followed by a space; no one condition is sufficient by itself. `BH` and `BL` contain the major and minor interface versions as Binary Coded Decimal values. [PDF p. 14](../_source/pages/page-014.md)

`AL` is a capability bitmap: bits 0 and 1 report Configuration Mechanism #1 and #2, bits 4 and 5 report Special Cycle generation through those mechanisms, and bits 2, 3, 6, and 7 are reserved and returned as zero. `CL` is the highest PCI bus number, with buses numbered from zero through that value. [PDF p. 15](../_source/pages/page-015.md)

For interface version 3.0 or later, `CH` reports support for configuration-register access ranges and optional functions, including interrupt routing, hardware interrupt assignment, Option ROM configuration-code execution, and DMTF CLP-style configuration data. Revision 3.0 and 3.1 require `CH` bits 0 and 1 to be set, but later revisions may not. [PDF p. 15](../_source/pages/page-015.md)

## Relationships

- It is the first host-interface operation used before relying on other Traditional PCI BIOS functions. [PDF p. 14](../_source/pages/page-014.md)
- Its `AL` bitmap describes hardware paths used to access Configuration Space and generate PCI Special Cycles. [PDF p. 15](../_source/pages/page-015.md)

## Evidence

- [Entry, exit, signature, and version contract, PDF p. 14](../_source/pages/page-014.md)
- [Capability bitmaps and bus range, PDF p. 15](../_source/pages/page-015.md)
