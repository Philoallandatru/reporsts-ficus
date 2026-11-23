---
type: Concept
title: PCI IRQ Routing
description: Traditional PCI BIOS exposes PCI INTx routing as a table of motherboard
  devices and slots, with one entry describing each device or slot's INTA# through
  INTD# routing possibilit...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI IRQ Routing

Traditional PCI BIOS exposes PCI INTx routing as a table of motherboard devices and slots, with one entry describing each device or slot's INTA# through INTD# routing possibilities and linkage. It also reports which IRQs are exclusively dedicated to PCI. [PDF pp. 18-20](../_source/pages/page-018.md)

## Structure or behavior

Each 16-byte routing entry contains Bus Number, Device Number, a link value and 16-bit IRQ bitmap for each of INTA# through INTD#, Slot Number, and an OEM-reserved byte. In an IRQ bitmap, bit N corresponds to IRQ N; one means routing is possible. Equal nonzero link values identify pins wire-ORed together, while link zero means no connection to the interrupt controller. [PDF p. 19](../_source/pages/page-019.md)

Slot Number zero identifies a motherboard device; nonzero values identify physical add-in slots using OEM-specific numbering that should correspond to visible slot labels. [PDF p. 19](../_source/pages/page-019.md)

The caller passes an `IRQRoutingExpansionsBuffer` containing `BufferSize` and a far `DataBuffer` pointer. If the buffer is too small, the BIOS returns `BUFFER_TOO_SMALL` and writes the required size; zero size indicates no PCI devices; success writes the returned byte count. The far-pointer representation varies across real mode, PM16, and PM32. [PDF p. 20](../_source/pages/page-020.md)

The caller initializes `BX` to `0000h`; the BIOS returns an IRQ bitmap there, setting a bit only when that IRQ is dedicated exclusively to PCI. The complete call may return `SUCCESSFUL`, `BUFFER_TOO_SMALL`, or `FUNC_NOT_SUPPORTED`. [PDF pp. 20-21](../_source/pages/page-020.md)

## Constraints and edge cases

Set PCI Hardware Interrupt is optional and intended only for a system-wide configuration utility or PNP operating system, not device drivers or Expansion ROM code. It changes routing immediately but does not persist it for the next boot. [PDF pp. 21-22](../_source/pages/page-021.md)

The caller must prevent resource conflicts, configure the interrupt controller for level triggering, and update affected devices' Interrupt Line registers. Changing one pin's routing also affects every wire-ORed pin with the same link value. [PDF p. 22](../_source/pages/page-022.md)

For assignment, `BX` carries bus, device, and function; `CL` selects INTA# through INTD# using `0Ah` through `0Dh`; and `CH` selects IRQ0 through IRQ15. [PDF p. 22](../_source/pages/page-022.md)

## Relationships

- PCI BIOS Present `CH` bits 2 and 3 advertise the routing-query and interrupt-assignment functions. [PDF p. 15](../_source/pages/page-015.md)
- Link values connect the routing table's topology to the side effects of changing an IRQ route. [PDF pp. 19, 22](../_source/pages/page-019.md)

## Evidence

- [Routing query and table introduction, PDF p. 18](../_source/pages/page-018.md)
- [IRQ Routing Table Entry and link semantics, PDF p. 19](../_source/pages/page-019.md)
- [Buffer and exclusive-IRQ bitmap, PDF p. 20](../_source/pages/page-020.md)
- [Routing-query call and assignment scope, PDF p. 21](../_source/pages/page-021.md)
- [Assignment behavior and entry registers, PDF p. 22](../_source/pages/page-022.md)
