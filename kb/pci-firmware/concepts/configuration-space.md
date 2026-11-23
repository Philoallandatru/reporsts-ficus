---
type: Concept
title: Configuration Space
description: Configuration Space is a PCI-specific address space used for device identification
  and for configuring devices into Memory and I/O spaces. It is distinct from those
  spaces. [PDF...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Configuration Space

Configuration Space is a PCI-specific address space used for device identification and for configuring devices into Memory and I/O spaces. It is distinct from those spaces. [PDF p. 8](../_source/pages/page-008.md)

## Structure or behavior

Each function of a multi-function PCI device has a separate Configuration Space. Vendor ID and Device ID fields jointly identify a device. [PDF pp. 8-9](../_source/pages/page-008.md)

Traditional PCI BIOS functions can generate accesses in Configuration Space; later sections define the concrete access mechanisms and extended register ranges. [PDF p. 10](../_source/pages/page-010.md)

## Relationships

- Located by a PCI Address plus a register offset.
- Accessed through legacy PCI BIOS mechanisms or enhanced memory-mapped mechanisms, depending on platform and device generation.

## Evidence

- [Definition and identity fields, PDF p. 8](../_source/pages/page-008.md)
- [PCI BIOS purpose, PDF p. 10](../_source/pages/page-010.md)
