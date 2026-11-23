---
type: Concept
title: Traditional PCI BIOS Configuration Access
description: Traditional PCI BIOS Configuration Access is the register-based interface
  for reading and writing a PCI function's Configuration Space through byte, word,
  and DWORD operations....
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Traditional PCI BIOS Configuration Access

Traditional PCI BIOS Configuration Access is the register-based interface for reading and writing a PCI function's Configuration Space through byte, word, and DWORD operations. The interface addresses a function by bus, device, and function number and supplies the register number in `DI`. [PDF pp. 24-29](../_source/pages/page-024.md)

## Why it matters

The interface provides a common legacy path to the first 256 bytes of Configuration Space and an optional, POST-oriented path to PCI Express Extended Configuration Space. It does not understand PCI Segment Groups and therefore reaches only PCI Segment Group 0. [PDF pp. 23-24](../_source/pages/page-023.md)

## Structure or behavior

The six operations are `READ_CONFIG_BYTE` (`08h`), `READ_CONFIG_WORD` (`09h`), `READ_CONFIG_DWORD` (`0Ah`), `WRITE_CONFIG_BYTE` (`0Bh`), `WRITE_CONFIG_WORD` (`0Ch`), and `WRITE_CONFIG_DWORD` (`0Dh`), all selected under `PCI_FUNCTION_ID` (`B1h`). Read results and write values use `CL`, `CX`, or `ECX` according to width. [PDF pp. 24-30](../_source/pages/page-024.md)

`BH` carries the bus number. In `BL`, the upper five bits carry the device number and the lower three bits carry the function number. `DI[11:0]` carries a register number from 0 through 4095, while `DI[15]` distinguishes an extended-register request above 255 from a conventional-register request. [PDF pp. 24-29](../_source/pages/page-024.md)

Word register numbers must be multiples of two, and DWORD register numbers must be multiples of four. Consequently, the largest conventional starting offsets are 255 for byte, 254 for word, and 252 for DWORD operations; the largest extended starting offsets are 4095, 4094, and 4092 respectively. [PDF pp. 24-29](../_source/pages/page-024.md)

Successful reads return data and `SUCCESSFUL`. Invalid register requests return `BAD_REGISTER_NUMBER`; requests for unsupported extended access return `FUNC_NOT_SUPPORTED`. The Carry Flag is cleared for success and set for error. Writes use the same documented status set without returning data. [PDF pp. 24-29](../_source/pages/page-024.md)

## Constraints and edge cases

The 32-bit service is entered with `CALL FAR`. Its `CS` and `DS` descriptors must cover the BIOS32-reported region and share a base; `ES` must be read/write with base zero and a 4-GiB limit so that it covers the 256-MiB PCI Express configuration BAR region. The caller must permit I/O-space access and supply at least 1 KiB of stack. [PDF p. 23](../_source/pages/page-023.md)

Firmware should use the PCI I/O Index/Data mechanism for offsets 0-255 and the PCI Express memory-mapped mechanism only for offsets 256 and above. Extended access assumes a memory-mapped configuration region below 4 GiB, and callers must avoid extended offsets on devices that do not support Extended Configuration Space. [PDF p. 23](../_source/pages/page-023.md)

Real-mode `INT 1Ah` extended reads are intended for internal firmware use during POST. After POST, software should use the location described by ACPI `MCFG` directly; firmware may return `FUNC_NOT_SUPPORTED` for an extended `INT 1Ah` read after POST. [PDF p. 24](../_source/pages/page-024.md)

When PCI BIOS Present reports the interface, register-access functions `06h` through `0Dh` are required below offset 256 during POST and at run time. Access above 255 is required only during POST; an implementation that retains it after POST must not change processor mode. [PDF p. 30](../_source/pages/page-030.md)

## Relationships

- Extends [Configuration Space](configuration-space.md) access from the conventional 256-byte region to the PCI Express 4-KiB region when supported.
- Uses the bus/device/function portion of a [PCI Address](pci-address.md), but cannot select a nonzero [PCI Segment Group](pci-segment-group.md). [PDF p. 23](../_source/pages/page-023.md)
- Relies on [PCI BIOS Present](pci-bios-present.md) to report whether extended configuration access is supported. [PDF p. 15](../_source/pages/page-015.md)

## Evidence

- [Protected-mode environment, segment-group limit, and access mechanisms, PDF p. 23](../_source/pages/page-023.md)
- [Real-mode extended-access lifecycle and byte-read contract, PDF p. 24](../_source/pages/page-024.md)
- [Width, alignment, register encoding, and status contracts, PDF pp. 25-29](../_source/pages/page-025.md)
- [Function identifiers and availability requirements, PDF p. 30](../_source/pages/page-030.md)
