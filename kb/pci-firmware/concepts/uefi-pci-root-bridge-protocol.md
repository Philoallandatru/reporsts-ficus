---
type: Concept
title: UEFI PCI Root Bridge Protocol
description: UEFI PCI Root Bridge Protocol is the host-side I/O abstraction through
  which a PCI Bus Driver issues PCI Memory, PCI I/O, and PCI Configuration cycles
  and performs bus-mastering...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# UEFI PCI Root Bridge Protocol

UEFI PCI Root Bridge Protocol is the host-side I/O abstraction through which a PCI Bus Driver issues PCI Memory, PCI I/O, and PCI Configuration cycles and performs bus-mastering DMA services. A UEFI PCI Root Bridge is represented by a device handle containing both Device Path Protocol and PCI Root Bridge Protocol instances. [PDF p. 32](../_source/pages/page-032.md)

## Why it matters

The protocol isolates platform-independent PCI code from a platform's system-memory map, including systems where host-processor MMIO addresses do not map identically to PCI-device addresses. [PDF p. 32](../_source/pages/page-032.md)

## Structure or behavior

The PCI Bus Driver consumes the root-bridge abstraction and creates child handles for discovered controllers; those child handles expose Device Path Protocol and PCI I/O Protocol to PCI Device Drivers. [PDF pp. 32-33](../_source/pages/page-032.md)

## Constraints and edge cases

Firmware must configure every Host Bridge, including bridges not connected to boot or console devices, because PCI specifications do not define the Host Bridge programming model. [PDF p. 35](../_source/pages/page-035.md)

## Relationships

- A foundational protocol of [UEFI PCI Services](uefi-pci-services.md).
- Host Bridges are later described to the operating system in ACPI using objects including `_CRS`, `_PRT`, `_BBN`, `_UID`, and, for a nonzero segment-group number, `_SEG`. [PDF p. 35](../_source/pages/page-035.md)

## Evidence

- [PCI Root Bridge Protocol definition, PDF p. 32](../_source/pages/page-032.md)
- [Host Bridge handoff requirements, PDF p. 35](../_source/pages/page-035.md)

