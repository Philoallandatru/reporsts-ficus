---
type: Concept
title: Generic ACPI PCI Slot Description
description: A generic ACPI PCI slot description represents one physical slot with
  eight ACPI device objects, one for each possible PCI function, so firmware can describe
  the slot for manage...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Generic ACPI PCI Slot Description

A generic ACPI PCI slot description represents one physical slot with eight ACPI device objects, one for each possible PCI function, so firmware can describe the slot for management or ACPI-based hot plug. [PDF p. 95](../_source/pages/page-095.md)

## Why it matters

The namespace model lets OSPM address every possible function in the slot even though the slot can contain only one device. [PDF p. 95](../_source/pages/page-095.md)

## Structure or behavior

Each of the eight objects uses `_ADR` to encode the shared device number and its distinct function number, from Function 0 through Function 7. Every object uses the same `_SUN` value to associate it with the same physical slot. [PDF p. 95](../_source/pages/page-095.md)

The specification example describes Slot 1 at Device 2 with `_ADR` values `0x00020000` through `0x00020007` and `_SUN` value `0x00000001`. [PDF p. 95](../_source/pages/page-095.md)

## Constraints and edge cases

All eight possible function objects must be listed for a described slot; the object set does not imply that eight separate devices can occupy the slot. [PDF p. 95](../_source/pages/page-095.md)

## Relationships

- `_ADR` supplies PCI device/function identity, while `_SUN` supplies the user-visible slot identity. [PDF p. 95](../_source/pages/page-095.md)
- The description can support ACPI-based PCI hot plug and slot manageability. [PDF p. 95](../_source/pages/page-095.md)

## Evidence

- [Generic slot requirements and namespace example, PDF p. 95](../_source/pages/page-095.md)
