---
type: Concept
title: Latency Tolerance Reporting
description: PCI `_DSM` Function 6 conveys platform maximum snoop and no-snoop latency
  encodings for PCI Express Latency Tolerance Reporting (LTR). [PDF p. 73](../_source/pages/page-073.md)
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Latency Tolerance Reporting

PCI `_DSM` Function 6 conveys platform maximum snoop and no-snoop latency encodings for PCI Express Latency Tolerance Reporting (LTR). [PDF p. 73](../_source/pages/page-073.md)

## Why it matters

Firmware supplies limits that should not be exceeded in normal operation, while the operating system calculates the accumulated path latency and programs the appropriate upstream LTR capability. [PDF p. 73](../_source/pages/page-073.md)

## Structure or behavior

The function uses lowest valid Revision ID 2, Function Index 6, and an empty package. It returns four integers: Maximum Snoop Latency Scale, Maximum Snoop Latency Value, Maximum No-Snoop Latency Scale, and Maximum No-Snoop Latency Value. [PDF p. 73](../_source/pages/page-073.md)

## Constraints and edge cases

The four values directly use the LTR Extended Capability field encoding; they are not raw durations without scale interpretation. [PDF p. 73](../_source/pages/page-073.md)

## Relationships

- This is Function 6 in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF p. 73](../_source/pages/page-073.md)

## Evidence

- [LTR responsibility and return package, PDF p. 73](../_source/pages/page-073.md)
