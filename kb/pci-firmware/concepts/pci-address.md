---
type: Concept
title: PCI Address
description: A PCI function is selected hierarchically by Segment Group Number, Bus
  Number, Device Number, and Function Number. The ranges defined here are 0-65535
  for segment groups, 0-255...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Address

A PCI function is selected hierarchically by Segment Group Number, Bus Number, Device Number, and Function Number. The ranges defined here are 0-65535 for segment groups, 0-255 for buses, 0-31 for devices, and 0-7 for functions. [PDF pp. 8-9](../_source/pages/page-008.md)

## Why it matters

The hierarchy separates a function's identity from a register offset within its Configuration Space. Bus numbers need only be unique inside one PCI Segment Group and may be reused across different groups. [PDF p. 9](../_source/pages/page-009.md)

## Relationships

- A Device ID and Vendor ID identify the device type/vendor; they are not routing coordinates.
- A multi-function device gives each function its own Configuration Space.
- A PCI Segment Group contains one or more PCI host bridges.

## Evidence

- [Explicit address-component definitions, PDF p. 8](../_source/pages/page-008.md)
- [Segment-group semantics, PDF p. 9](../_source/pages/page-009.md)
