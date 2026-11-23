---
type: Concept
title: Operating System Hot Plug (`OSHP`)
description: '`OSHP` is the ACPI control method that transfers an SHPC from firmware
  control to an operating system with native SHPC support. [PDF p. 96](../_source/pages/page-096.md)'
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Operating System Hot Plug (`OSHP`)

`OSHP` is the ACPI control method that transfers an SHPC from firmware control to an operating system with native SHPC support. [PDF p. 96](../_source/pages/page-096.md)

## Why it matters

Legacy platforms may use ACPI firmware to operate an SHPC, but native operating-system access requires a clean ownership handoff that stops firmware register access and restores interrupt and wake signaling. [PDF p. 96](../_source/pages/page-096.md)

## Structure or behavior

A platform that uses ACPI firmware to operate an SHPC must provide `OSHP` for each firmware-controlled SHPC. A native SHPC operating system must execute the method before accessing that controller's registers and again after returning from hibernation. [PDF p. 96](../_source/pages/page-096.md)

After `OSHP` executes, firmware must not access SHPC registers. Firmware must also restore signals such as System Interrupt or `PME#` if it had redirected them for firmware servicing. Repeated calls after control has transferred must succeed without further action. [PDF p. 96](../_source/pages/page-096.md)

## Constraints and edge cases

A platform may implement both `OSHP` and `_OSC`, but an operating system that understands `_OSC` preferentially uses `_OSC`. [PDF p. 96](../_source/pages/page-096.md)

The implementation guidance recommends Configuration Space DWORD Select/DWORD Data access for a PCI-to-PCI bridge SHPC, while a host-bridge register block can be covered by an ACPI memory operation region. [PDF p. 96](../_source/pages/page-096.md)

## Relationships

- `OSHP` is a focused SHPC handoff mechanism; [`_OSC`](osc.md) is the broader PCI host-hierarchy capability and control negotiation method. [PDF p. 96](../_source/pages/page-096.md)
- Both methods implement a [Firmware/Operating System Handoff](firmware-os-handoff.md). [PDF p. 96](../_source/pages/page-096.md)

## Evidence

- [`OSHP` requirements and implementation guidance, PDF p. 96](../_source/pages/page-096.md)
