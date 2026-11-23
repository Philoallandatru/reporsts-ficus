---
type: Concept
title: UEFI Expansion ROM
description: A UEFI Expansion ROM is a PCI Expansion ROM image with Code Type 3 that
  stores UEFI images such as UEFI drivers according to the UEFI specification. [PDF
  p. 122](../_source/page...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# UEFI Expansion ROM

A UEFI Expansion ROM is a PCI Expansion ROM image with Code Type 3 that stores UEFI images such as UEFI drivers according to the UEFI specification. [PDF p. 122](../_source/pages/page-122.md)

## Why it matters

It marks a distinct execution model from the PC-compatible Code Type 0 ROM flow. [PDF p. 122](../_source/pages/page-122.md)

## Structure or behavior

The PCI Firmware specification delegates the storage format and behavior of UEFI images in PCI Expansion ROMs to UEFI Specification Version 2.4, Section 13.4.2. [PDF p. 122](../_source/pages/page-122.md)

## Constraints and edge cases

The Code Type 0 rules in PCI Firmware Specification Section 5.2.1 do not apply to UEFI Expansion ROMs. [PDF p. 122](../_source/pages/page-122.md)

## Relationships

- It is a Code Type 3 form of [PCI Expansion ROM](pci-expansion-rom.md). [PDF p. 122](../_source/pages/page-122.md)
- Its execution model is separate from [PC-Compatible Expansion ROM Initialization](pc-compatible-expansion-rom-initialization.md). [PDF p. 122](../_source/pages/page-122.md)

## Evidence

- [UEFI Expansion ROM boundary, PDF p. 122](../_source/pages/page-122.md)
