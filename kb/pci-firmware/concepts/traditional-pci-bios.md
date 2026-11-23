---
type: Concept
title: Traditional PCI BIOS
description: Traditional PCI BIOS is the PC-compatible software interface for PCI-specific
  hardware operations, especially Configuration Space and Special Cycle operations.
  It supports sever...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Traditional PCI BIOS

Traditional PCI BIOS is the PC-compatible software interface for PCI-specific hardware operations, especially Configuration Space and Special Cycle operations. It supports several x86 execution modes. [PDF p. 10](../_source/pages/page-010.md)

## Structure or behavior

Sixteen-bit callers use Interrupt `1Ah`; 32-bit protected-mode callers use a protected-mode entry point and `CALL FAR`. The PCI BIOS function code is `B1h`, with sub-function codes selecting operations. Status is returned through the Carry Flag and function-specific registers. [PDF pp. 10-11](../_source/pages/page-010.md)

The routines pass arguments in x86 registers, preserve registers and flags not used for return values, are re-entrant, and require 1024 bytes of stack. The caller must provide sufficient privilege for interrupt and I/O-space access. [PDF pp. 10-11](../_source/pages/page-010.md)

## Constraints and edge cases

Legacy boot support requires INTx routing. MSI or MSI-X may become available to the operating system after BIOS boot. [PDF p. 11](../_source/pages/page-011.md)

## Relationships

- BIOS32 Service Directory discovers the 32-bit PCI BIOS entry point.
- PCI BIOS Present validates that the function set exists and reports version/access information.

## Evidence

- [Functional model and calling conventions, PDF p. 10](../_source/pages/page-010.md)
- [16/32-bit entry paths and interrupt support, PDF p. 11](../_source/pages/page-011.md)
