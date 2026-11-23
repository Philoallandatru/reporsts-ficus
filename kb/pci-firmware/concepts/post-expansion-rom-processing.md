---
type: Concept
title: POST Expansion ROM Processing
description: POST Expansion ROM Processing is the firmware procedure that discovers
  a device ROM, selects a compatible image, validates device identity and checksum,
  copies the image to RAM,...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# POST Expansion ROM Processing

POST Expansion ROM Processing is the firmware procedure that discovers a device ROM, selects a compatible image, validates device identity and checksum, copies the image to RAM, and disables ROM decoding before code-type-specific initialization. [PDF pp. 103-104](../_source/pages/page-103.md)

## Why it matters

It defines the trust and selection boundary between a PCI device's potentially multi-image ROM and the execution environment that POST firmware is prepared to initialize. [PDF pp. 103-104](../_source/pages/page-103.md)

## Structure or behavior

POST examines PCI functions individually for an Expansion ROM Base Address register, temporarily enables the ROM at an unused memory address, and tests the first two bytes for the `AA55h` signature value. Device examination and initialization order are unspecified, and separate functions of a multi-function device may each implement a ROM register. [PDF p. 103](../_source/pages/page-103.md)

Firmware follows each image header's nonzero PCI Data Structure pointer, requires the target signature `PCIR`, and compares Code Type with the expected execution environment. If the type is unsuitable and Last Image indicates another image, Image Length in 512-byte units advances from the current image's start to the next image. [PDF p. 103](../_source/pages/page-103.md)

For the selected image, Vendor ID must match the device. If Device ID differs, Revision 3.0-or-later non-UEFI images may match through the Device List Pointer and its `0000h`-terminated list. Firmware then considers Maximum Run-Time Image Length, validates the image checksum using Current Image Size, copies the amount identified by Image Length into RAM, and disables the Expansion ROM Base Address register. [PDF p. 104](../_source/pages/page-104.md)

## Constraints and edge cases

Firmware must not inspect Revision 3-only fields until it confirms PCI Data Structure Revision 3 or later. Code Type 3 (UEFI) does not support the Device List Pointer. When both a PCI 2.1 image and a Revision 3.0-or-later image match the same device, POST must prefer the later image and use the older image only if no later one is found. [PDF p. 104](../_source/pages/page-104.md)

The header stores signature bytes as `55h AAh`, while the POST procedure names their little-endian 16-bit value `AA55h`; these are two notations for the same two bytes. [PDF pp. 99, 103](../_source/pages/page-099.md)

## Relationships

- Image traversal uses the [PCI Data Structure](pci-data-structure.md) Image Length and Last Image Indicator. [PDF p. 103](../_source/pages/page-103.md)
- Alternate Device ID matching uses the [PCI Expansion ROM Device List](pci-expansion-rom-device-list.md). [PDF p. 104](../_source/pages/page-104.md)
- A selected Code Type 0 image continues through [PC-Compatible Expansion ROM Initialization](pc-compatible-expansion-rom-initialization.md). [PDF pp. 104-106](../_source/pages/page-104.md)

## Evidence

- [Discovery and image traversal, PDF p. 103](../_source/pages/page-103.md)
- [Matching, validation, copying, and ROM disablement, PDF p. 104](../_source/pages/page-104.md)
