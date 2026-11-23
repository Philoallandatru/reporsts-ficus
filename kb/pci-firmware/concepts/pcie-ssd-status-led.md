---
type: Concept
title: PCIe SSD Status LED Interface
description: The PCIe SSD Status LED `_DSM` is a four-function ACPI interface through
  which OSPM discovers, reads, and requests platform-controlled storage status indications
  for an embedded...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCIe SSD Status LED Interface

The PCIe SSD Status LED `_DSM` is a four-function ACPI interface through which OSPM discovers, reads, and requests platform-controlled storage status indications for an embedded PCIe function or add-in PCI Express slot. [PDF pp. 89-90](../_source/pages/page-089.md)

## Why it matters

The interface supplies a common status vocabulary for PCIe SSD indicators. OSPM should prefer it when present, otherwise it can use Native PCIe Enclosure Management or SCSI Enclosure Services when available. [PDF p. 89](../_source/pages/page-089.md)

## Structure or behavior

The interface uses UUID `5D524D9D-FFF9-4D4B-8CB7-747ED51E194D`, Revision ID 1, and Function Index 0 through 3. Function 0 returns `{0x0F}` to advertise all four functions; Function 1 reports supported LED states, Function 2 reads current states, and Function 3 requests new states. [PDF pp. 89-91](../_source/pages/page-089.md)

Functions 1–3 return at least four status bytes: a two-byte General Status Code followed by one-byte function-specific and vendor-specific codes. General status 0 is success; any nonzero value is failure, with defined categories for unsupported operation, invalid input, communication error, and the two extended error-code classes. [PDF p. 90](../_source/pages/page-090.md)

The common 32-bit LED-state bitmap reserves bits 0–1 and 12–31. Bits 2–11 represent OK, Locate, Fail, Rebuild, Predicted Failure Analysis, Hot Spare, Critical Array, Failed Array, Invalid Device, and Disabled states. Function 1 uses set bits to grant OSPM control of individual states, while Function 2 reports their current values. [PDF pp. 91-93](../_source/pages/page-091.md)

Function 3 takes the requested bitmap and returns status plus the resulting bitmap. A request with no bits set must succeed; when function-specific error bit 0 is set, the platform disregarded some or all requested changes and OSPM must inspect the returned state. [PDF pp. 94-95](../_source/pages/page-094.md)

## Constraints and edge cases

The `_DSM` must be under the ACPI object for the embedded PCIe device/function or under the ACPI PCIe description for the add-in slot. Functions 4 through `0xFFFF` are reserved. [PDF p. 89](../_source/pages/page-089.md)

The state descriptions are intentionally permissive (`may mean`): for example, OK does not distinguish absent from unpowered hardware, and Disabled can mean slot power is removed. [PDF p. 92](../_source/pages/page-092.md)

## Relationships

- This is a separate `_DSM` UUID from the general [PCI Device Specific Method (`_DSM`)](pci-dsm.md) function catalog. [PDF p. 89](../_source/pages/page-089.md)
- NPEM and SES are fallback management mechanisms when this `_DSM` is absent. [PDF p. 89](../_source/pages/page-089.md)

## Evidence

- [Interface UUID and function catalog, PDF p. 89](../_source/pages/page-089.md)
- [Common status and Function 0, PDF p. 90](../_source/pages/page-090.md)
- [Supported-state bitmap, PDF pp. 91-92](../_source/pages/page-091.md)
- [Read and set operations, PDF pp. 93-95](../_source/pages/page-093.md)
