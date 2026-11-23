---
type: Concept
title: DPC Containment Port Location
description: PCI `_DSM` Function `0Dh` lets an Error Disconnect Recovery-aware operating
  system identify the child port that actually entered DPC containment when firmware
  sends the recovery...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# DPC Containment Port Location

PCI `_DSM` Function `0Dh` lets an Error Disconnect Recovery-aware operating system identify the child port that actually entered DPC containment when firmware sends the recovery notification to a parent port. [PDF p. 87](../_source/pages/page-087.md)

## Why it matters

A recovery notification can target a Root Port or Switch Downstream Port above the containment event. The function removes that ambiguity so software can inspect and recover the affected downstream path. [PDF p. 87](../_source/pages/page-087.md)

## Structure or behavior

The method uses the PCI `_DSM` UUID, lowest valid Revision ID 5, Function Index `0Dh`, and an empty Arg3 package. Its integer result encodes Function in bits 2:0, Device in bits 7:3, Bus in bits 15:8, and operation status in bit 31, where 0 means success and 1 means failure; all other bits are reserved. [PDF pp. 87-88](../_source/pages/page-087.md)

The child port inherits the parent's Segment Group Number. If the target parent does not implement the function, the operating system treats the notification target itself as the port that experienced containment. [PDF p. 87](../_source/pages/page-087.md)

## Constraints and edge cases

The function may be placed only under a DPC-capable PCI Express Root Port or Switch Downstream Port. When a port implements it, child devices below that port cannot instantiate the same function. [PDF p. 87](../_source/pages/page-087.md)

## Relationships

- This is Function `0Dh` in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF p. 87](../_source/pages/page-087.md)
- It follows Error Disconnect Recovery notification and complements [DPC and Hot-Plug Surprise Control](dpc-hot-plug-surprise-control.md), Function `0Ch`. [PDF pp. 86-87](../_source/pages/page-086.md)

## Evidence

- [Placement, arguments, and fallback behavior, PDF p. 87](../_source/pages/page-087.md)
- [Return encoding, PDF p. 88](../_source/pages/page-088.md)
