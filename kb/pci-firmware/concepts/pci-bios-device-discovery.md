---
type: Concept
title: PCI BIOS Device Discovery
description: Traditional PCI BIOS provides indexed searches that locate the Nth PCI
  function matching either a Vendor ID plus Device ID or a three-byte Class Code.
  Successful calls return th...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI BIOS Device Discovery

Traditional PCI BIOS provides indexed searches that locate the Nth PCI function matching either a Vendor ID plus Device ID or a three-byte Class Code. Successful calls return the Bus Number in `BH`, with Device Number in the upper five bits of `BL` and Function Number in its lower three bits. [PDF pp. 16-17](../_source/pages/page-016.md)

## Why it matters

Callers enumerate all matches by starting the index in `SI` at zero and incrementing it until `DEVICE_NOT_FOUND` is returned. The Vendor/Device search also returns `BAD_VENDOR_ID` when the Vendor ID is all ones. [PDF pp. 16-17](../_source/pages/page-016.md)

## Constraints and edge cases

The Vendor ID input range excludes `FFFFh`. Locations returned by a successful Vendor/Device search are the actual coordinates that direct PCI I/O mechanisms must use if the caller bypasses the `INT 1Ah` routines. [PDF p. 16](../_source/pages/page-016.md)

Both calls use Carry Flag as completion status: set indicates error and clear indicates success. [PDF pp. 16-17](../_source/pages/page-016.md)

## Relationships

- Vendor ID and Device ID search identifies a particular device type. [PDF p. 16](../_source/pages/page-016.md)
- Class Code search identifies functions by functional class rather than vendor-specific identity. [PDF p. 17](../_source/pages/page-017.md)
- Returned Bus, Device, and Function fields form the legacy PCI BIOS portion of a PCI Address. [PDF pp. 16-17](../_source/pages/page-016.md)

## Evidence

- [Find PCI Device contract, PDF p. 16](../_source/pages/page-016.md)
- [Find PCI Class Code contract, PDF p. 17](../_source/pages/page-017.md)
