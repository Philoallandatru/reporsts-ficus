---
type: Concept
title: PCI Express Slot Number Tokens
description: PCI Express Slot Number Tokens are the ordered bit ranges returned by
  PCI `_DSM` Function 2 to decompose monolithic ACPI or PCI Express slot numbers into
  meaningful hardware ele...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Express Slot Number Tokens

PCI Express Slot Number Tokens are the ordered bit ranges returned by PCI `_DSM` Function 2 to decompose monolithic ACPI or PCI Express slot numbers into meaningful hardware elements such as chassis, cabinet, I/O tray, module, and slot. [PDF pp. 65-66](../_source/pages/page-065.md)

## Why it matters

Tokenization lets software present topology-aware slot labels without prescribing the final user-interface format. The interpretation applies to PCI devices below the ACPI object containing the method unless a lower namespace object overrides it. [PDF p. 65](../_source/pages/page-065.md)

## Structure or behavior

Function 2 uses the common PCI `_DSM` UUID and lowest valid Revision ID 1. It may appear on any device in the `\_SB` scope and returns at least one four-item token package containing Source ID, Token ID, start bit, and end bit. [PDF pp. 65-66](../_source/pages/page-065.md)

Source IDs select `_SUN`, the PCI-to-PCI Bridge Chassis ID, or the PCI Express Physical Slot Number. Standard Token IDs identify chassis through slot elements; Token IDs `80h`–`FFh` are vendor-specific. [PDF p. 66](../_source/pages/page-066.md)

PCI `_DSM` Function 3 maps a vendor-specific Token ID to locale-tagged UTF-16 descriptions. It must exist in the same context as Function 2 and accepts only Token IDs in the `80h`–`FFh` range. [PDF p. 67](../_source/pages/page-067.md)

## Constraints and edge cases

Function 3 returns language identifiers in RFC 3066 form and explicitly permits `zh-chs` and `zh-cht` aliases for `zh-Hans` and `zh-Hant`. Software may fall back from a sub-language to the primary language. [PDF p. 67](../_source/pages/page-067.md)

## Relationships

- Function 2 interprets numbers supplied by `_SUN` or PCI bridge/PCI Express registers; it does not replace those number sources. [PDF pp. 65-66](../_source/pages/page-065.md)
- Function 3 supplies display text only for vendor-specific token kinds defined by Function 2. [PDF p. 67](../_source/pages/page-067.md)

## Evidence

- [Scope, override, and arguments, PDF p. 65](../_source/pages/page-065.md)
- [Token package and example, PDF p. 66](../_source/pages/page-066.md)
- [Vendor-specific localized strings, PDF p. 67](../_source/pages/page-067.md)
