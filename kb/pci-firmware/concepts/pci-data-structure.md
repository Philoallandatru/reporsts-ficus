---
type: Concept
title: PCI Data Structure (`PCIR`)
description: The PCI Data Structure is the DWORD-aligned, `PCIR`-identified metadata
  record within a PCI Expansion ROM image that describes the image's identity, size,
  code type, revision, a...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Data Structure (`PCIR`)

The PCI Data Structure is the DWORD-aligned, `PCIR`-identified metadata record within a PCI Expansion ROM image that describes the image's identity, size, code type, revision, and chaining state. [PDF pp. 99-101](../_source/pages/page-099.md)

## Why it matters

System firmware uses this record to recognize an image, match it to a device and execution environment, find the next image, and locate optional interfaces defined by newer structure revisions. [PDF pp. 100-103](../_source/pages/page-100.md)

## Structure or behavior

The record must be within the first 64 KiB of its ROM image and DWORD aligned. Its four-byte signature is `PCIR`, with `P` at offset 0, followed by Vendor ID, Device ID, Device List Pointer, structure length and revision, Class Code, Image Length, vendor ROM revision, Code Type, Last Image Indicator, maximum run-time image length, and two optional-entry pointers. [PDF p. 100](../_source/pages/page-100.md)

Image Length and Maximum Run-Time Image Length are little-endian two-byte values in 512-byte units. Revision 3 adds the maximum run-time length so firmware can determine whether the initialized image fits available system memory. [PDF p. 101](../_source/pages/page-101.md)

Code Type values 0, 1, 2, and 3 designate Intel x86 PC-AT-compatible code, Open Firmware, HP PA-RISC, and UEFI respectively; values `4`–`FFh` are reserved. Last Image Indicator bit 7 equals 1 for the final image and 0 when another image follows; bits 0–6 are reserved. [PDF p. 101](../_source/pages/page-101.md)

## Constraints and edge cases

The Device List Pointer, Maximum Run-Time Image Length, Configuration Utility Code Header pointer, and DMTF CLP entry-point pointer exist only in Revision 3.0 or later. For UEFI Code Type 3, the Device List and both optional-entry pointers must be `0000h`. [PDF pp. 100-102](../_source/pages/page-100.md)

The Device List Pointer is relative to the beginning of the PCI Data Structure. The Configuration Utility and DMTF CLP pointers are relative to the beginning of the Expansion ROM image. [PDF pp. 100, 102](../_source/pages/page-100.md)

## Relationships

- The image header's pointer locates this structure from the start of the [PCI Expansion ROM](pci-expansion-rom.md) image. [PDF p. 99](../_source/pages/page-099.md)
- A nonzero Device List Pointer locates a [PCI Expansion ROM Device List](pci-expansion-rom-device-list.md). [PDF pp. 100, 102](../_source/pages/page-100.md)

## Evidence

- [Field layout and initial definitions, PDF p. 100](../_source/pages/page-100.md)
- [Revision, length, code type, and chaining fields, PDF p. 101](../_source/pages/page-101.md)
- [Optional pointers, PDF p. 102](../_source/pages/page-102.md)
