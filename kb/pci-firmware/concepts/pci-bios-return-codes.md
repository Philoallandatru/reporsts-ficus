---
type: Concept
title: Traditional PCI BIOS Return Codes
description: Traditional PCI BIOS Return Codes are the status values returned in `AH`
  by PCI BIOS functions. The defined values are `SUCCESSFUL` (`00h`), `FUNC_NOT_SUPPORTED`
  (`81h`), `BAD_V...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Traditional PCI BIOS Return Codes

Traditional PCI BIOS Return Codes are the status values returned in `AH` by PCI BIOS functions. The defined values are `SUCCESSFUL` (`00h`), `FUNC_NOT_SUPPORTED` (`81h`), `BAD_VENDOR_ID` (`83h`), `DEVICE_NOT_FOUND` (`86h`), `BAD_REGISTER_NUMBER` (`87h`), `SET_FAILED` (`88h`), and `BUFFER_TOO_SMALL` (`89h`). [PDF p. 31](../_source/pages/page-031.md)

## Why it matters

The codes provide one shared status vocabulary across discovery, configuration access, interrupt routing, and other Traditional PCI BIOS operations. [PDF pp. 16-31](../_source/pages/page-016.md)

## Structure or behavior

`SUCCESSFUL` reports completion. The remaining values distinguish an unavailable function, invalid vendor identifier, unsuccessful device search, invalid register number, failed state change, or insufficient caller buffer. [PDF p. 31](../_source/pages/page-031.md)

## Constraints and edge cases

The table defines numeric identifiers, while each function's contract determines which codes can occur and what output registers remain meaningful. [PDF pp. 16-30](../_source/pages/page-016.md)

## Relationships

- Used by [Traditional PCI BIOS](traditional-pci-bios.md) functions.
- Configuration-space operations specifically use `SUCCESSFUL`, `BAD_REGISTER_NUMBER`, and `FUNC_NOT_SUPPORTED`. [PDF pp. 24-30](../_source/pages/page-024.md)

## Evidence

- [Return Code List, PDF p. 31](../_source/pages/page-031.md)

