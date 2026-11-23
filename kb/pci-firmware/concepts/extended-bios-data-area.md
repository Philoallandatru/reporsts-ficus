---
type: Concept
title: Extended BIOS Data Area Usage
description: Extended BIOS Data Area (EBDA) Usage is the discouraged fallback by which
  Expansion ROM code obtains permanent memory below 1 MiB when PMM services are unavailable.
  [PDF p. 114]...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Extended BIOS Data Area Usage

Extended BIOS Data Area (EBDA) Usage is the discouraged fallback by which Expansion ROM code obtains permanent memory below 1 MiB when PMM services are unavailable. [PDF p. 114](../_source/pages/page-114.md)

## Why it matters

EBDA is a shared, movable low-memory buffer; direct use requires coordinated pointer, size, and conventional-memory accounting that PMM normally centralizes. [PDF p. 114](../_source/pages/page-114.md)

## Structure or behavior

The ROM detects EBDA through the nonzero segment pointer at `40:0Eh`. If absent, it reduces the size at `40:13h` by 1 KiB, records the new segment at `40:0Eh`, and initializes the first EBDA byte to the size in KiB. [PDF p. 114](../_source/pages/page-114.md)

To expand EBDA, code rounds the request to KiB, rejects a resulting size above 64 KiB, disables interrupts while moving the existing buffer downward, updates `40:0Eh` and the EBDA size byte, and subtracts the allocation from `40:13h`. [PDF p. 114](../_source/pages/page-114.md)

## Constraints and edge cases

All EBDA references must re-read the pointer at `40:0Eh`, because expansion moves the segment while offsets remain stable. The value at `40:13h` is neither a reliable presence test nor a size source for EBDA. [PDF p. 114](../_source/pages/page-114.md)

## Relationships

- [POST Memory Manager Allocation](post-memory-manager-allocation.md) is the preferred mechanism for below-1-MiB memory. [PDF p. 114](../_source/pages/page-114.md)

## Evidence

- [EBDA fallback algorithm and invariants, PDF p. 114](../_source/pages/page-114.md)
