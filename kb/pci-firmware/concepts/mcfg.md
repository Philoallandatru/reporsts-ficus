---
type: Concept
title: MCFG
description: '`MCFG` is the ACPI table that reports processor-relative Enhanced Configuration
  Access Mechanism base addresses for non-hot-removable PCI Segment Groups, or bus
  ranges within th...'
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# MCFG

`MCFG` is the ACPI table that reports processor-relative Enhanced Configuration Access Mechanism base addresses for non-hot-removable PCI Segment Groups, or bus ranges within them, that are available at boot on PC-compatible systems. [PDF pp. 38, 40](../_source/pages/page-040.md)

## Why it matters

It gives system software the boot-time mapping from a Segment Group and bus range to memory-mapped Configuration Space. A range described exclusively by `MCFG` is non-relocatable and non-hot-removable for that boot. [PDF p. 38](../_source/pages/page-038.md)

## Structure or behavior

The table begins with the ACPI `MCFG` header and contains one or more 16-byte allocation structures. Each allocation supplies a 64-bit Base Address, 16-bit PCI Segment Group Number, Start Bus Number, End Bus Number, and four reserved bytes. [PDF pp. 41-42](../_source/pages/page-041.md)

An allocation's base address is defined relative to bus 0 even when the host bridge starts at a higher bus number. System software calculates the supported memory interval from that base and the Start/End Bus Numbers, without assuming the preceding address interval is usable. [PDF pp. 42, 44](../_source/pages/page-044.md)

Multiple entries may identify different non-overlapping bus ranges in one Segment Group, allowing distinct host bridges to use different base addresses. [PDF pp. 42, 45](../_source/pages/page-042.md)

## Constraints and edge cases

`MCFG` must not describe hot-pluggable PCI Segment Groups; those use `_CBA`. At least one allocation entry corresponds to each Segment Group represented by the table. Segment Group 0 may omit `_SEG` when it is the system's only group. [PDF pp. 40-42](../_source/pages/page-041.md)

The reported memory-mapped configuration range must be reserved through ACPI as a motherboard resource when the operating system cannot reserve it natively. [PDF p. 41](../_source/pages/page-041.md)

## Relationships

- Describes the [Enhanced Configuration Access Mechanism](enhanced-configuration-access.md).
- Uses [PCI Segment Group](pci-segment-group.md) and bus-range identity.
- Complements [`_CBA`](cba.md), which handles hot-plug-capable host bridges and runtime reevaluation.

## Evidence

- [`MCFG` purpose and Segment Group association, PDF p. 40](../_source/pages/page-040.md)
- [`MCFG` header and reservation rules, PDF p. 41](../_source/pages/page-041.md)
- [Allocation structure and multiple-entry rules, PDF p. 42](../_source/pages/page-042.md)
- [System-software address calculation, PDF p. 44](../_source/pages/page-044.md)

