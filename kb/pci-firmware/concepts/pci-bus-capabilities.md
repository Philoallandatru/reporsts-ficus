---
type: Concept
title: PCI Bus Capabilities Structure
description: The PCI Bus Capabilities Structure is the 16-byte, bus-type-specific
  record returned through PCI `_DSM` Function 4 to describe a PCI root bus's capabilities
  and current operatin...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Bus Capabilities Structure

The PCI Bus Capabilities Structure is the 16-byte, bus-type-specific record returned through PCI `_DSM` Function 4 to describe a PCI root bus's capabilities and current operating mode when no upstream bridge configuration registers exist to report them. [PDF pp. 68-70](../_source/pages/page-068.md)

## Why it matters

PCI-to-PCI bridges expose comparable information in configuration-space headers and capabilities, but ACPI exposes a root bus without such bridge registers. The `_DSM` therefore supplies the missing root-bus description dynamically. [PDF p. 68](../_source/pages/page-068.md)

## Structure or behavior

A root bus has exactly one Bus Capabilities Structure, aligned to a four-byte boundary. The only defined bus type is Type 1 for PCI; Type 0 and values 2 or greater are reserved. [PDF p. 68](../_source/pages/page-068.md)

The Type 1 structure contains Type, Length, Attributes, Current Speed/Mode, Supported Speeds/Modes, Voltage, and reserved bytes. Length is 16 bytes; capability attributes cover a 64-bit secondary interface, PCI-X Mode 1 ECC, Device ID Message forwarding, and an OBFF/`WAKE#` wiring case not reported by Device Capabilities 2. [PDF pp. 69-70](../_source/pages/page-069.md)

Function 4 is placed under the ACPI object representing a PCI or PCI-X root bus identified by `_HID` or `_CID` `PNP0A03`. It returns method status plus a buffer header and the type-dependent Bus Capabilities Structure. [PDF p. 71](../_source/pages/page-071.md)

The call uses UUID `E5C937D0-3553-4D7A-9117-EA4D19C3434D`, lowest valid Revision ID 1, Function Index 4, and an empty package. Its two-item result contains an integer operation status and a buffer whose header carries Version, Status, total Length, and the Bus Capabilities Structure beginning at byte offset 8. [PDF p. 71](../_source/pages/page-071.md)

## Constraints and edge cases

The Supported Speeds/Modes field is a bitmap, whereas Current Speed/Mode is a single encoding; consumers must not interpret them as the same representation. Reserved fields and unused bits are required to remain reserved. [PDF pp. 69-70](../_source/pages/page-069.md)

The source describes the method return as an ACPI Buffer while immediately defining a two-item package; consumers should treat the explicit package layout as authoritative only after resolving this wording ambiguity. [PDF p. 71](../_source/pages/page-071.md)

## Relationships

- This is Function 4 in the shared [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace, with lowest valid Revision ID 1. [PDF pp. 63, 71](../_source/pages/page-063.md)
- The structure complements the [ACPI PCI Host Bridge Description](acpi-pci-host-bridge.md) by reporting root-bus operating characteristics rather than address windows or routing. [PDF pp. 47, 68](../_source/pages/page-068.md)

## Evidence

- [Purpose, alignment, and bus types, PDF p. 68](../_source/pages/page-068.md)
- [PCI structure fields, PDF pp. 69-70](../_source/pages/page-069.md)
- [Function 4 binding and return wrapper, PDF p. 71](../_source/pages/page-071.md)
