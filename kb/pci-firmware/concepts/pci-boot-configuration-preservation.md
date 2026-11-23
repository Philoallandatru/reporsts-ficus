---
type: Concept
title: PCI Boot Configuration Preservation
description: PCI `_DSM` Function 5 tells an operating system whether firmware-assigned
  bus numbers, I/O ports, memory ranges, BARs, and bridge windows must be preserved
  or may be rebalanced....
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Boot Configuration Preservation

PCI `_DSM` Function 5 tells an operating system whether firmware-assigned bus numbers, I/O ports, memory ranges, BARs, and bridge windows must be preserved or may be rebalanced. [PDF pp. 72-73](../_source/pages/page-072.md)

## Why it matters

The optional indication defines the resource-reconfiguration boundary between firmware and the operating system for a device or hierarchy. [PDF p. 72](../_source/pages/page-072.md)

## Structure or behavior

The function uses lowest valid Revision ID 2, Function Index 5, and an empty package. It returns integer 0 when firmware assignments must be preserved and integer 1 when the operating system may reconfigure or rebalance them. [PDF pp. 72-73](../_source/pages/page-072.md)

A Function 5 on a device applies directly; otherwise the nearest enclosing ACPI namespace implementation applies. On a bridge it covers the bridge and its downstream hierarchy until overridden by a lower Function 5. [PDF p. 72](../_source/pages/page-072.md)

## Constraints and edge cases

Even under preservation, devices with invalid BAR, window, or bus-number settings may receive resources; constrained preserved layouts can reduce hot-plug capability. Host-bridge root resources remain governed by `_CRS` and, when supplied, `_PRS`/`_SRS`. [PDF pp. 72-73](../_source/pages/page-072.md)

## Relationships

- This is Function 5 in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF p. 72](../_source/pages/page-072.md)
- It refines the [Firmware/Operating System Handoff](firmware-os-handoff.md) for PCI resource assignments. [PDF pp. 72-73](../_source/pages/page-072.md)

## Evidence

- [Scope, inheritance, and arguments, PDF p. 72](../_source/pages/page-072.md)
- [Return semantics, PDF p. 73](../_source/pages/page-073.md)
