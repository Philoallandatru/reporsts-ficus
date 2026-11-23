---
type: Concept
title: PCI Expansion ROM
description: A PCI Expansion ROM is a device-associated ROM containing one or more
  chained code images for device-specific initialization and optional system boot
  functions. [PDF p. 98](../_...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Expansion ROM

A PCI Expansion ROM is a device-associated ROM containing one or more chained code images for device-specific initialization and optional system boot functions. [PDF p. 98](../_source/pages/page-098.md)

## Why it matters

It lets a PCI device carry firmware for multiple processor or system architectures while using a common image-discovery format compatible with existing Intel x86 Expansion ROM headers. [PDF p. 98](../_source/pages/page-098.md)

## Structure or behavior

A physical ROM may contain any number of executable or interpretive images. Each image begins on a 512-byte boundary, starts with a PCI Expansion ROM header, and identifies whether another image follows. [PDF p. 98](../_source/pages/page-098.md)

Every image header begins with bytes `55h AAh`. At offsets `18h`–`19h`, a two-byte little-endian pointer is relative to the beginning of that image and locates its [PCI Data Structure](pci-data-structure.md), which must lie within the image's first 64 KiB. [PDF p. 99](../_source/pages/page-099.md)

PCI Expansion ROM code is copied to RAM and initialized there rather than executed in place. Code conforming to version 3.0 or later can then move itself to its final RAM execution location, supporting dynamic initialization and run-time sizing. [PDF p. 98](../_source/pages/page-098.md)

## Constraints and edge cases

The start of every image depends on the sizes of the preceding images; the final image is marked through the Last Image Indicator in its PCI Data Structure. [PDF pp. 98, 101](../_source/pages/page-098.md)

## Relationships

- Each image has its own header and [`PCIR` PCI Data Structure](pci-data-structure.md). [PDF pp. 99-100](../_source/pages/page-099.md)
- The PCI Data Structure's Image Length and Last Image Indicator drive traversal of a multi-image ROM. [PDF pp. 100-101](../_source/pages/page-100.md)

## Evidence

- [ROM execution and multi-image organization, PDF p. 98](../_source/pages/page-098.md)
- [Expansion ROM header, PDF p. 99](../_source/pages/page-099.md)
