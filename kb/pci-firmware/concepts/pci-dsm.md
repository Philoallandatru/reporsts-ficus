---
type: Concept
title: PCI Device Specific Method (`_DSM`)
description: The PCI Device Specific Method is the ACPI `_DSM` binding identified
  by UUID `E5C937D0-3553-4D7A-9117-EA4D19C3434D`; it exposes PCI device-specific functions
  to OSPM and device...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Device Specific Method (`_DSM`)

The PCI Device Specific Method is the ACPI `_DSM` binding identified by UUID `E5C937D0-3553-4D7A-9117-EA4D19C3434D`; it exposes PCI device-specific functions to OSPM and device drivers. [PDF pp. 62-63](../_source/pages/page-062.md)

## Why it matters

The binding provides one versioned namespace for functions including slot information, bus capabilities, boot-configuration preservation, readiness timing, D3cold auxiliary-power limits, DPC/hot-plug control, and vendor-specific TPH queries. [PDF p. 63](../_source/pages/page-063.md)

## Structure or behavior

Each function has an Initial Revision ID, while this specification defines Current Revision ID 6. A function call is valid only from its initial revision through the current revision; firmware must use the passed revision's expected behavior when it supports multiple revisions. [PDF p. 62](../_source/pages/page-062.md)

Function 0 is the discovery operation. OSPM first invokes it with the highest revision it knows; an empty or all-zero response means the UUID is unknown, while a response containing only bit 0 means the UUID is known but that revision is unsupported, so OSPM probes lower revisions. [PDF p. 63](../_source/pages/page-063.md)

Revision 3.3 assigns Functions 1 through 14 (`0Eh`) to slot information, slot-number tokenization and labels, bus capabilities, configuration preservation, latency and readiness controls, power/reset controls, containment coordination, and vendor-specific TPH discovery. Each function's valid revisions begin at its Initial Revision ID in Table 4-7. [PDF p. 63](../_source/pages/page-063.md)

## Constraints and edge cases

Firmware must support the same Revision ID across all functions it implements. OSPM must invoke all nonzero functions with the revision selected through Function 0; an invalid revision causes firmware to take no action on inputs and makes returned data unusable. [PDF pp. 62-63](../_source/pages/page-062.md)

The Current Revision ID advances when a function is added or an existing function changes operationally, although revisions may make backward-compatible changes. Firmware may support only a subset of valid revisions and reports the supported function set through Function 0 for the probed revision. [PDF p. 62](../_source/pages/page-062.md)

## Relationships

- This is an ACPI device method consumed by OSPM or a device driver, distinct from host-hierarchy feature ownership negotiation through [`_OSC`](osc.md). [PDF p. 62](../_source/pages/page-062.md)
- The DPC and Hot-Plug Surprise Control function participates in the `_OSC` DPC ownership and surprise-removal model. [PDF p. 60](../_source/pages/page-060.md)
- Functions 1–4 define [PCI Express Slot Information](pci-express-slot-information.md), [PCI Express Slot Number Tokens](pci-express-slot-number.md), localized vendor token labels, and the [PCI Bus Capabilities Structure](pci-bus-capabilities.md). [PDF pp. 63-71](../_source/pages/page-063.md)
- Functions `0Ah`–`0Ch` define the [D3cold Auxiliary Power Limit](d3cold-aux-power-limit.md), [PERST# Assertion Delay](perst-assertion-delay.md), and [DPC and Hot-Plug Surprise Control](dpc-hot-plug-surprise-control.md). [PDF pp. 79-84](../_source/pages/page-079.md)

## Evidence

- [PCI `_DSM` revision model, PDF p. 62](../_source/pages/page-062.md)
- [Function discovery and definition table, PDF p. 63](../_source/pages/page-063.md)
