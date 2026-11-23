---
type: Concept
title: Vendor-Specific TPH Steering Tag
description: PCI `_DSM` Function `0Eh` reports the nonzero Steering Tag value a PCI
  Express Endpoint should use for a platform-vendor-specific Transaction Processing
  Hints (TPH) feature. [PD...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Vendor-Specific TPH Steering Tag

PCI `_DSM` Function `0Eh` reports the nonzero Steering Tag value a PCI Express Endpoint should use for a platform-vendor-specific Transaction Processing Hints (TPH) feature. [PDF p. 88](../_source/pages/page-088.md)

## Why it matters

A Root Complex can recognize vendor-specific Steering Tag encodings in upstream Memory TLPs. The method gives operating-system software the platform value needed to configure an Endpoint that advertises Device Specific Mode support in its TPH Requester Capability. [PDF p. 88](../_source/pages/page-088.md)

## Structure or behavior

The method uses the PCI `_DSM` UUID, lowest valid Revision ID 6, and Function Index `0Eh`. Arg3 is an integer containing Vendor ID in bits 15:0 and the queried vendor-specific Feature ID in bits 31:16; the integer return is the Steering Tag value, which must be nonzero when the platform implements that feature. [PDF p. 88](../_source/pages/page-088.md)

## Constraints and edge cases

The function applies only to a `_DSM` under a PCI Express Root Port or Root Complex Integrated Endpoint. The specification does not define a separate status wrapper for this function. [PDF p. 88](../_source/pages/page-088.md)

## Relationships

- This is Function `0Eh` in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF p. 88](../_source/pages/page-088.md)
- Endpoint eligibility is advertised through the TPH Extended Capability Structure's Device Specific Mode Supported bit. [PDF p. 88](../_source/pages/page-088.md)

## Evidence

- [Purpose, placement, arguments, and return, PDF p. 88](../_source/pages/page-088.md)
