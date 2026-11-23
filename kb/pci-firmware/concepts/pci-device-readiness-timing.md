---
type: Concept
title: PCI Device Readiness Timing
description: PCI `_DSM` Functions 8 and 9 coordinate post-reset responsibility and
  device-specific delay reductions before the operating system first accesses a PCI
  device. [PDF pp. 76-78](....
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Device Readiness Timing

PCI `_DSM` Functions 8 and 9 coordinate post-reset responsibility and device-specific delay reductions before the operating system first accesses a PCI device. [PDF pp. 76-78](../_source/pages/page-076.md)

## Why it matters

They avoid duplicate delays after Sx resume and permit shorter initialization waits where platform knowledge safely overrides baseline PCI Express or form-factor timing. [PDF pp. 76-78](../_source/pages/page-076.md)

## Structure or behavior

Function 8 uses lowest valid Revision ID 3 and returns 1 when hardware or firmware has supplied the post-power-on reset delay for the entire PCI subsystem below a host bus; 0 retains the legacy operating-system delay responsibility. [PDF pp. 76-77](../_source/pages/page-076.md)

Function 9 uses lowest valid Revision ID 3 and returns five microsecond values for Conventional Reset, `DL_Up`, FLR, D3hot-to-D0, and VF Enable waits. Each value applies only to the ACPI device object on which the function is placed. [PDF pp. 77-78](../_source/pages/page-077.md)

## Constraints and edge cases

Function 8 is valid only in PCI host-bus scope and covers integrated Root Complex devices in that hierarchy. Firmware remains responsible for delays after runtime power gating, while an operating system that independently applies Conventional Reset must enforce the resulting delay itself. [PDF p. 76](../_source/pages/page-076.md)

Function 9 values may only reduce required or device-reported latency; values above specification minima are ignored. Firmware values override Configuration Ready indicators, FRS/DRS notifications, and Readiness Time Reporting values for the corresponding delay; `Ones` means no override is desired. [PDF pp. 77-78](../_source/pages/page-077.md)

## Relationships

- These are Functions 8 and 9 in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF pp. 76-78](../_source/pages/page-076.md)
- Function 8 establishes hierarchy-wide responsibility, while Function 9 supplies per-device duration overrides. [PDF pp. 76-78](../_source/pages/page-076.md)

## Evidence

- [Post-power-on delay ownership, PDF pp. 76-77](../_source/pages/page-076.md)
- [Readiness override rules and package, PDF pp. 77-78](../_source/pages/page-077.md)
