---
type: Concept
title: PCI Device Naming Hint
description: PCI `_DSM` Function 7 supplies an instance number and optional chassis-facing
  Unicode name that an operating system can use when labeling PCI or PCI Express devices
  and slots. [...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Device Naming Hint

PCI `_DSM` Function 7 supplies an instance number and optional chassis-facing Unicode name that an operating system can use when labeling PCI or PCI Express devices and slots. [PDF pp. 73-74](../_source/pages/page-073.md)

## Why it matters

Stable platform-provided ordering lets an operating system assign lower labels to otherwise similar devices with lower instance numbers, while the optional name can match the physical chassis label. [PDF pp. 74-75](../_source/pages/page-074.md)

## Structure or behavior

The function uses lowest valid Revision ID 2, Function Index 7, and no Arg3 value. It returns a two-element package containing a mandatory instance number and a string; an absent name is represented by a null string. [PDF p. 74](../_source/pages/page-074.md)

The instance number and any populated string must each be unique under `\_SB`; instance numbers need not be sequential. [PDF p. 74](../_source/pages/page-074.md)

## Constraints and edge cases

The method applies to ACPI-described embedded devices/functions or ACPI slot objects. Naming of multifunction devices installed in slots and devices hot-added by the operating system remains operating-system-specific. [PDF p. 74](../_source/pages/page-074.md)

## Relationships

- This is Function 7 in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF p. 74](../_source/pages/page-074.md)

## Evidence

- [Package semantics and placement, PDF pp. 73-74](../_source/pages/page-073.md)
- [Ordering example, PDF p. 75](../_source/pages/page-075.md)
