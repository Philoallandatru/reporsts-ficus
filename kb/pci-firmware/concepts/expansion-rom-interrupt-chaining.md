---
type: Concept
title: Expansion ROM Interrupt Chaining
description: Expansion ROM Interrupt Chaining is the shared, level-triggered PCI interrupt
  convention in which each ROM-installed ISR preserves and invokes the previous vector
  until control...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Expansion ROM Interrupt Chaining

Expansion ROM Interrupt Chaining is the shared, level-triggered PCI interrupt convention in which each ROM-installed ISR preserves and invokes the previous vector until control reaches the default System BIOS handler. [PDF p. 116](../_source/pages/page-116.md)

## Why it matters

Multiple devices can share one PCI interrupt, so no ROM handler may terminate the chain or incorrectly mask a line needed by another participant. [PDF p. 116](../_source/pages/page-116.md)

## Structure or behavior

A ROM saves the original vector before installing its own. Invocation order is the reverse of installation order, and the final BIOS handler handles regular or spurious interrupts and issues the appropriate EOI, including to master/slave controllers for IRQ 8 or above. [PDF p. 116](../_source/pages/page-116.md)

With a Revision 3.0-or-later BIOS, a ROM chains onward and does not issue EOI itself. Without such BIOS support, the compatibility behavior is for the ROM to issue EOI and execute IRET. Firmware supplies at least a 4-KiB stack during POST; the same minimum is recommended for run-time callers. [PDF p. 116](../_source/pages/page-116.md)

## Constraints and edge cases

After installing its ISR a ROM may unmask a previously masked interrupt. Neither later ROM handlers nor the default BIOS handler should mask that shared level-triggered line. [PDF p. 116](../_source/pages/page-116.md)

## Relationships

- ROMs discover the relevant firmware revision with [PCI BIOS Present](pci-bios-present.md). [PDF p. 116](../_source/pages/page-116.md)
- Relocated vectors must target the final address selected by [Expansion ROM Run-Time Placement](expansion-rom-runtime-placement.md). [PDF p. 112](../_source/pages/page-112.md)

## Evidence

- [ISR chaining, EOI ownership, and stack requirement, PDF p. 116](../_source/pages/page-116.md)
