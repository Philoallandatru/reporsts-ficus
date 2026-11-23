---
type: Concept
title: Enhanced Configuration Access Mechanism
description: The Enhanced Configuration Access Mechanism is the memory-mapped mechanism
  used on PC-compatible systems to access PCI configuration registers. For PCI Express
  and PCI-X Mode 2,...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Enhanced Configuration Access Mechanism

The Enhanced Configuration Access Mechanism is the memory-mapped mechanism used on PC-compatible systems to access PCI configuration registers. For PCI Express and PCI-X Mode 2, it is the only mechanism for Extended Configuration Space offsets 256 through 4095. [PDF pp. 38-39](../_source/pages/page-038.md)

## Why it matters

Its platform-specific base addresses connect a PCI address and register offset to a processor-visible memory address, allowing an operating system to reach the full 4-KiB configuration space. [PDF p. 39](../_source/pages/page-039.md)

## Structure or behavior

ACPI communicates boot-time, non-hot-removable base addresses through `MCFG`. The `_CBA` method reports base addresses for segment groups or ranges that require runtime description, including hot-added PCI components and hot-plug-capable segment groups. [PDF p. 38](../_source/pages/page-038.md)

The first 256 bytes may be accessed through either the legacy `CF8/CFC` mechanism or the enhanced mechanism. For the memory address encoding, bus, device, function, extended-register, and register fields select the target; a full 256-bus segment group occupies a 256-MiB window when each function has 4 KiB. [PDF p. 39](../_source/pages/page-039.md)

The address layout assigns one MiB per bus: address bits select bus, device, function, and the 4-KiB register offset. A chipset may implement less than the full 256-MiB window, and multiple host bridges may divide a segment group's bus numbers into non-overlapping, non-contiguous ranges. [PDF pp. 39-40](../_source/pages/page-039.md)

## Constraints and edge cases

Ranges described exclusively by `MCFG` are non-relocatable and non-hot-removable for the current boot. The mechanism can traverse heterogeneous PCI, PCI-X, and PCI Express hierarchies, but the extended region is defined for PCI Express and PCI-X Mode 2 functions. [PDF pp. 38-39](../_source/pages/page-038.md)

For non-Mode 2 PCI-X and PCI devices, only the first 256 bytes are accessible. Host bridges in one segment group need not decode contiguous bus ranges. [PDF p. 40](../_source/pages/page-040.md)

## Relationships

- Extends [Configuration Space](configuration-space.md) access beyond the conventional 256 bytes.
- Base-address descriptions are associated with a [PCI Segment Group](pci-segment-group.md) or a bus range within one. [PDF p. 38](../_source/pages/page-038.md)
- [MCFG](mcfg.md) describes boot-time non-hot-removable ranges; [`_CBA`](cba.md) describes a host bridge's runtime-discoverable base address.
- Traditional PCI BIOS extended accesses use this mechanism during POST. [PDF p. 23](../_source/pages/page-023.md)

## Evidence

- [ACPI `MCFG` and `_CBA` roles, PDF p. 38](../_source/pages/page-038.md)
- [Address encoding and configuration-space coverage, PDF p. 39](../_source/pages/page-039.md)
