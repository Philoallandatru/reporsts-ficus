---
type: Concept
title: PCI Expansion ROM Device List
description: The PCI Expansion ROM Device List is a zero-terminated array of 16-bit
  Device IDs that lets one non-UEFI Revision 3.0-or-later ROM image declare support
  for multiple PCI devices...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Expansion ROM Device List

The PCI Expansion ROM Device List is a zero-terminated array of 16-bit Device IDs that lets one non-UEFI Revision 3.0-or-later ROM image declare support for multiple PCI devices. [PDF p. 102](../_source/pages/page-102.md)

## Why it matters

Without a Device List, an image supports only the single Device ID stored directly in its PCI Data Structure; the list makes one image reusable across several device identities. [PDF p. 102](../_source/pages/page-102.md)

## Structure or behavior

A nonzero Device List Pointer is relative to the beginning of the `PCIR` PCI Data Structure and points to consecutive two-byte Device IDs. A `0000h` entry terminates the list. [PDF p. 102](../_source/pages/page-102.md)

## Constraints and edge cases

The mechanism is defined for PCI Data Structure Revision 3.0 or later only when Code Type is not 3 (UEFI). A zero Device List Pointer means the image supports only the PCI Data Structure's Device ID. [PDF p. 102](../_source/pages/page-102.md)

## Relationships

- The pointer and primary Device ID are fields of the [PCI Data Structure (`PCIR`)](pci-data-structure.md). [PDF pp. 100, 102](../_source/pages/page-100.md)
- UEFI images cannot use this list through the Revision 3 structure because their Device List Pointer must be `0000h`. [PDF pp. 100, 102](../_source/pages/page-100.md)

## Evidence

- [Device List semantics and table format, PDF p. 102](../_source/pages/page-102.md)
