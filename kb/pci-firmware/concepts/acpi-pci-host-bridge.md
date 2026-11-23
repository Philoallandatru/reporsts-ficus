---
type: Concept
title: ACPI PCI Host Bridge Description
description: An ACPI PCI host bridge description identifies the hierarchy type with
  a Plug-and-Play ID and exposes the objects system software needs to locate Configuration
  Space and manage...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# ACPI PCI Host Bridge Description

An ACPI PCI host bridge description identifies the hierarchy type with a Plug-and-Play ID and exposes the objects system software needs to locate Configuration Space and manage bridge resources. [PDF pp. 45-47](../_source/pages/page-046.md)

## Why it matters

The description lets OSPM distinguish conventional PCI/PCI-X from PCI Express or PCI-X Mode 2, while retaining compatibility with operating systems that recognize only the older host-bridge ID. [PDF pp. 45-46](../_source/pages/page-045.md)

## Structure or behavior

`PNP0A03` identifies PCI/PCI-X host bridge hierarchies. `PNP0A08` identifies PCI Express and PCI-X Mode 2 host bridges as supporting 4-KiB extended Configuration Space; a device using `PNP0A08` as `_HID` must also provide `PNP0A03` as `_CID` for legacy compatibility. [PDF pp. 45-46](../_source/pages/page-046.md)

Memory-mapped configuration access is reported separately through `MCFG` or `_CBA`; `PNP0A08` alone does not assert that mapping. For PCI-X Mode 2, OSPM uses `_DSM` to determine whether extended configuration capability is currently enabled. [PDF p. 46](../_source/pages/page-046.md)

Bridge resource objects include `_CRS` for current I/O, memory, and bus ranges; configurable bridges add `_PRS` for possible settings and `_SRS` for applying an allocation. `_BBN` selects the boot bus for PCI_Config Operation Region access, and `_SEG` identifies the PCI Segment Group. [PDF p. 47](../_source/pages/page-047.md)

PCI INTx routing cannot be inferred from PCI register space. Every PCI host bridge therefore supplies `_PRT`; when namespace-described Root Ports have their own `_PRT`, OSPM evaluates and uses those routes. ACPI does not participate in MSI or MSI-X use. [PDF p. 47](../_source/pages/page-047.md)

## Constraints and edge cases

Legacy `CF8/CFCh` access is Segment Group unaware and supports at most 256 bus numbers. A platform that must support legacy operating systems or x86 BIOS Option ROMs may therefore need non-overlapping bus numbers across Segment Groups. [PDF p. 45](../_source/pages/page-045.md)

## Relationships

- [`MCFG`](mcfg.md) and [`_CBA`](cba.md) provide enhanced-configuration base addresses.
- `_SEG` associates the bridge with a [PCI Segment Group](pci-segment-group.md).
- `_CRS`, `_PRS`, and `_SRS` describe and control bridge resources. [PDF p. 47](../_source/pages/page-047.md)
- `_PRT` maps legacy PCI INTx pins to interrupt controllers; MSI and MSI-X remain PCI-defined mechanisms outside ACPI routing. [PDF p. 47](../_source/pages/page-047.md)
- [`_OSC`](osc.md) negotiates operating-system feature support and control for the hierarchy rooted at the host bridge. [PDF p. 48](../_source/pages/page-048.md)

## Evidence

- [Host-bridge PNP IDs and multiple-bridge considerations, PDF p. 45](../_source/pages/page-045.md)
- [`PNP0A08` compatibility and meaning, PDF p. 46](../_source/pages/page-046.md)
- [Resource, boot-bus, and Segment Group objects, PDF p. 47](../_source/pages/page-047.md)
