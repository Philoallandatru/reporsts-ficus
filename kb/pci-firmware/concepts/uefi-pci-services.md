---
type: Concept
title: UEFI PCI Services
description: UEFI PCI Services are the UEFI driver-model protocols and abstractions
  used to enumerate and operate Conventional PCI, PCI-X, and PCI Express devices during
  the pre-boot environ...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# UEFI PCI Services

UEFI PCI Services are the UEFI driver-model protocols and abstractions used to enumerate and operate Conventional PCI, PCI-X, and PCI Express devices during the pre-boot environment. UEFI itself supplies platform information and boot/runtime services through tables and callable interfaces. [PDF p. 32](../_source/pages/page-032.md)

## Why it matters

They replace processor-specific legacy entry conventions with a processor-agnostic environment for PCI bus drivers, PCI device drivers, and operating-system boot. [PDF p. 32](../_source/pages/page-032.md)

## Structure or behavior

A PCI Bus Driver manages PCI buses and creates child handles containing Device Path Protocol and PCI I/O Protocol instances. A PCI Device Driver uses PCI I/O Protocol to manage a controller and may produce an I/O abstraction needed to boot a UEFI-compliant operating system. [PDF p. 33](../_source/pages/page-033.md)

PCI I/O Protocol supports configuration-space addresses up to 4 GiB and therefore covers the 4-KiB PCI-X Mode 2 and PCI Express Extended Configuration Space. During pre-boot UEFI uses polling and a single timer interrupt rather than `INTx`, MSI, or MSI-X for UEFI drivers. [PDF p. 33](../_source/pages/page-033.md)

UEFI also defines EFI Byte Code (`EBC`) as a platform- and CPU-independent virtual-machine instruction set, and Graphics Output Protocol (`GOP`) as a display abstraction that removes the firmware requirement for legacy VGA and `INT 10h`. [PDF p. 33](../_source/pages/page-033.md)

## Constraints and edge cases

The presence of a UEFI driver in firmware or an Expansion ROM does not guarantee that it is loaded, executed, or permitted to manage a device; UEFI drivers also do not participate in PCI hot plug. [PDF p. 36](../_source/pages/page-036.md)

## Relationships

- Uses [UEFI PCI Root Bridge Protocol](uefi-pci-root-bridge-protocol.md) below the PCI Bus Driver.
- Establishes the pre-boot side of [Firmware/Operating System Handoff](firmware-os-handoff.md).
- Operates on [Configuration Space](configuration-space.md), Memory Space, and I/O Space. [PDF pp. 32-33](../_source/pages/page-032.md)

## Evidence

- [UEFI service and driver-model overview, PDF p. 32](../_source/pages/page-032.md)
- [PCI Driver Model and related protocols, PDF p. 33](../_source/pages/page-033.md)

