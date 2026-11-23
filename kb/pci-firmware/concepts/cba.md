---
type: Concept
title: '`_CBA`'
description: '`_CBA` (Memory-mapped Configuration Base Address) is an optional ACPI
  control method under a host bridge object that returns its processor-relative, 64-bit
  Enhanced Configuratio...'
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# `_CBA`

`_CBA` (Memory-mapped Configuration Base Address) is an optional ACPI control method under a host bridge object that returns its processor-relative, 64-bit Enhanced Configuration Access Mechanism base address as an Integer. It is used for hot-plug-capable host bridges that add a bus range or a PCI Segment Group on PC-compatible systems. [PDF p. 43](../_source/pages/page-043.md)

## Why it matters

Unlike the boot-static `MCFG` table, `_CBA` lets an operating system discover or reevaluate configuration-space mappings as host bridges are added or their resources are rebalanced. [PDF pp. 38, 43](../_source/pages/page-043.md)

## Structure or behavior

The method takes no arguments and returns the base address. The containing host bridge must also provide `_SEG`; its `_CRS` identifies the corresponding bus-number range. Different host bridges in one Segment Group may return different base addresses. [PDF p. 43](../_source/pages/page-043.md)

The returned base is relative to bus 0. System software derives the supported address interval from the host bridge's bus range in `_CRS`. When `_PRS` and `_SRS` permit resource rebalancing, the operating system reevaluates `_CBA` whenever it evaluates `_CRS`. [PDF pp. 43-44](../_source/pages/page-043.md)

## Constraints and edge cases

`_CBA` and `_BBN` must execute before PCI_Config Operation Region access below the bridge is enabled, so neither method may itself reference such a downstream PCI_Config Operation Region. Non-hot-pluggable host bridges use `MCFG` instead. [PDF p. 43](../_source/pages/page-043.md)

## Relationships

- Describes the [Enhanced Configuration Access Mechanism](enhanced-configuration-access.md).
- Complements [MCFG](mcfg.md).
- Relies on ACPI host-bridge objects described by [ACPI PCI Host Bridge Description](acpi-pci-host-bridge.md).

## Evidence

- [`_CBA` placement, return value, dependencies, and reevaluation, PDF p. 43](../_source/pages/page-043.md)
- [System-software address calculation, PDF p. 44](../_source/pages/page-044.md)

