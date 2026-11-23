---
type: Concept
title: Expansion ROM Configuration Utility
description: An Expansion ROM Configuration Utility is an optional, separately identified
  code block that system firmware can preserve during INIT and execute later in POST
  at the user's req...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Expansion ROM Configuration Utility

An Expansion ROM Configuration Utility is an optional, separately identified code block that system firmware can preserve during INIT and execute later in POST at the user's request. [PDF pp. 116-118](../_source/pages/page-116.md)

## Why it matters

Firmware-managed execution avoids conflicting hotkeys and unconditional delays while giving all ROM configuration tools a consistent selection point. Delayed execution is preferred over legacy or hybrid self-invocation during INIT. [PDF p. 117](../_source/pages/page-117.md)

## Structure or behavior

A PCI Data Structure pointer identifies the optional utility header. Firmware copies the utility into temporary memory before INIT; the ROM shrinks to its final run-time size while the utility remains available. Until the end of POST, the utility may update configuration data in the not-yet-write-protected run-time image, but it must not enlarge that image and must repair its checksum. [PDF p. 117](../_source/pages/page-117.md)

The three execution models are legacy (no managed header), hybrid (INIT and firmware may each run the utility), and delayed execution (only firmware runs it later). Firmware support is optional, so the ROM checks it through PCI BIOS Present. [PDF pp. 117-118](../_source/pages/page-117.md)

Firmware enters the utility by far call in Big Real Mode and the utility returns by far return. Registers supply Bus/Device/Function, console-redirection state, a cleared status byte, the PMM entry point, and the run-time ROM address; returned `BH` bit 0 requests a reset. [PDF p. 118](../_source/pages/page-118.md)

## Constraints and edge cases

The utility need not preserve registers, must use firmware interrupt services for input/output, and can assume basic devices are initialized. Firmware owns how users select among available utilities; the specification does not define the selection UI. [PDF pp. 118-119](../_source/pages/page-118.md)

When `BL` bit 0 indicates Console Redirection, the utility must retain the firmware-selected text video mode, accept input only through keyboard `Int 16h`, and send all output through `Int 10h` rather than writing a video buffer directly. [PDF p. 119](../_source/pages/page-119.md)

The utility is a contiguous, self-contained code block whose leading header contains a one-byte length in 512-byte units, a 40-byte null-terminated ASCII identifier field, and a one-byte header revision whose defined value is 1. The header and utility code count toward the PCI Data Structure's Image Length. [PDF pp. 119-120](../_source/pages/page-119.md)

## Relationships

- [PCI BIOS Present](pci-bios-present.md) reports whether firmware implements managed configuration code. [PDF p. 118](../_source/pages/page-118.md)
- The utility receives the [POST Memory Manager Allocation](post-memory-manager-allocation.md) entry point directly. [PDF p. 118](../_source/pages/page-118.md)
- Its updates occur within the retained image established by [PC-Compatible Expansion ROM Initialization](pc-compatible-expansion-rom-initialization.md). [PDF p. 117](../_source/pages/page-117.md)

## Evidence

- [Configuration-code motivation, PDF p. 116](../_source/pages/page-116.md)
- [Lifecycle and execution models, PDF p. 117](../_source/pages/page-117.md)
- [Call contract and firmware services, PDF p. 118](../_source/pages/page-118.md)
- [Console-redirection rules and utility header, PDF p. 119](../_source/pages/page-119.md)
- [Header inclusion in image length, PDF p. 120](../_source/pages/page-120.md)
