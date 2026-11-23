---
type: Concept
title: Expansion ROM SM CLP Entry Point
description: The Expansion ROM SM CLP Entry Point is an optional Code Type 0 interface
  through which system firmware can send DMTF Server Management Command Line Protocol
  commands to a PCI d...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Expansion ROM SM CLP Entry Point

The Expansion ROM SM CLP Entry Point is an optional Code Type 0 interface through which system firmware can send DMTF Server Management Command Line Protocol commands to a PCI device or its children during pre-boot configuration. [PDF p. 120](../_source/pages/page-120.md)

## Why it matters

It lets a remote management session configure a device before INIT while leaving discovery, enumeration, and translation of SM CLP UFiTs to system firmware. The ROM can persist settings for use by its INIT code on the current or later boots. [PDF pp. 120, 122](../_source/pages/page-120.md)

## Structure or behavior

Firmware invokes the entry point by far call in Big Real Mode and may call it repeatedly. `AX` identifies the ROM's source Bus/Device/Function; `ES:EDI` points to a null-terminated command line, and `DS:ESI` points to a response buffer of at least 4 KiB. The ROM may use command target data when one entry point supports multiple devices. [PDF p. 120](../_source/pages/page-120.md)

On return, `AL` carries SM CLP command status. For processing failure (`AL = 2`), `AH` carries a processing error; for execution failure (`AL = 3`), the upper half of `EAX` carries an execution code and bit 31 distinguishes an OEM-specific value from an SM CLP probable-cause value. The input pointers and command text are preserved, and the response defaults to required null-terminated `keyword=value` output. [PDF p. 121](../_source/pages/page-121.md)

## Constraints and edge cases

The ROM may assume at least a 4-KiB stack and 128 KiB of extended PMM memory. The command target is scoped to the PCI device's address space rather than the containing computer system. Firmware support and ROM implementation are independently optional; absence in the ROM is represented by a null PCI Data Structure pointer. [PDF pp. 120-122](../_source/pages/page-120.md)

Configuration performed after the Expansion ROM INIT code has run may require a reboot before it takes effect. [PDF p. 122](../_source/pages/page-122.md)

## Relationships

- [PCI BIOS Present](pci-bios-present.md) reports whether firmware supports calling this interface. [PDF p. 121](../_source/pages/page-121.md)
- The [PCI Data Structure](pci-data-structure.md) carries the optional entry-point pointer. [PDF p. 122](../_source/pages/page-122.md)
- The entry point runs before [PC-Compatible Expansion ROM Initialization](pc-compatible-expansion-rom-initialization.md) in the normal remote-configuration sequence. [PDF p. 122](../_source/pages/page-122.md)

## Evidence

- [Input contract and environment, PDF p. 120](../_source/pages/page-120.md)
- [Output contract and firmware discovery, PDF p. 121](../_source/pages/page-121.md)
- [Optional pointer and boot sequence, PDF p. 122](../_source/pages/page-122.md)
