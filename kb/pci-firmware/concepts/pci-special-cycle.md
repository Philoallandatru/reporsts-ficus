---
type: Concept
title: PCI Special Cycle
description: A PCI Special Cycle is a bus-wide operation that the Traditional PCI
  BIOS can generate on a caller-selected PCI bus with caller-supplied 32-bit data.
  [PDF p. 18](../_source/page...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Special Cycle

A PCI Special Cycle is a bus-wide operation that the Traditional PCI BIOS can generate on a caller-selected PCI bus with caller-supplied 32-bit data. [PDF p. 18](../_source/pages/page-018.md)

## Structure or behavior

The Generate Special Cycle call takes the bus number in `BH` and Special Cycle data in `EDX`. It returns `SUCCESSFUL` or `FUNC_NOT_SUPPORTED`, with Carry Flag clear for success and set for error. [PDF p. 18](../_source/pages/page-018.md)

## Relationships

PCI BIOS Present reports separately whether Special Cycle generation is supported through Configuration Mechanism #1 or #2 in `AL` bits 4 and 5. [PDF p. 15](../_source/pages/page-015.md)

## Evidence

- [PCI BIOS capability bits, PDF p. 15](../_source/pages/page-015.md)
- [Generate Special Cycle call, PDF p. 18](../_source/pages/page-018.md)
