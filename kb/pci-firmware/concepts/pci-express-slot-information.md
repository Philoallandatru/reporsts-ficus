---
type: Concept
title: PCI Express Slot Information
description: PCI Express Slot Information is PCI `_DSM` Function 1, used by firmware
  to describe a motherboard slot's supported link widths, physical slot type, and
  sideband signals when sta...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Express Slot Information

PCI Express Slot Information is PCI `_DSM` Function 1, used by firmware to describe a motherboard slot's supported link widths, physical slot type, and sideband signals when static SMBIOS Type 9 data is inadequate for a dynamically changing platform. Hardware-reported information takes precedence if a direct operating-system mechanism becomes available. [PDF pp. 63-64](../_source/pages/page-063.md)

## Why it matters

The method gives management software a dynamic description of slot capabilities, including link-width downshift possibilities rather than only the maximum or negotiated link width. [PDF p. 64](../_source/pages/page-064.md)

## Structure or behavior

The method uses PCI `_DSM` UUID `E5C937D0-3553-4D7A-9117-EA4D19C3434D`, lowest valid Revision ID 1, and Function Index 1. It is located beneath the virtual PCI-to-PCI bridge object for the Root Port or Switch Port that creates the motherboard slot. [PDF pp. 63-64](../_source/pages/page-063.md)

Its return value is a two-item package: an operation status and a three-integer slot-information package. The integers describe supported link widths, slot type, and the presence of SMBus and `WAKE#` signals. [PDF pp. 64-65](../_source/pages/page-064.md)

## Constraints and edge cases

Multiple link-width bits and multiple signal bits may be set. Maximum and negotiated link width are not supplied by this method and instead come from PCI Express hardware. [PDF p. 64](../_source/pages/page-064.md)

## Relationships

- This function belongs to the common [PCI Device Specific Method (`_DSM`)](pci-dsm.md) revision and discovery model. [PDF pp. 62-64](../_source/pages/page-062.md)
- It provides information comparable to SMBIOS Type 9 while supporting platforms whose slot characteristics can change dynamically. [PDF p. 63](../_source/pages/page-063.md)

## Evidence

- [Function definition and placement, PDF pp. 63-64](../_source/pages/page-063.md)
- [Return package and slot fields, PDF pp. 64-65](../_source/pages/page-064.md)
