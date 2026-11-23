---
type: Concept
title: PCI Segment Group
description: A PCI Segment Group is a system-firmware-managed logical collection of
  PCI buses or bus segments, used by the operating system. It has no required physical
  identity. [PDF p. 9](...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Segment Group

A PCI Segment Group is a system-firmware-managed logical collection of PCI buses or bus segments, used by the operating system. It has no required physical identity. [PDF p. 9](../_source/pages/page-009.md)

## Why it matters

Segment groups allow a system to exceed 256 total buses by reusing bus numbers in different groups. Bus numbers must remain unique within a group. Every system has at least Segment Group 0, and a group contains one or more PCI host bridges. [PDF p. 9](../_source/pages/page-009.md)

## Relationships

- Segment Group Number selects the group and ranges from 0 to 65535. [PDF p. 9](../_source/pages/page-009.md)
- Bus Number selects a bus within that group. [PDF p. 9](../_source/pages/page-009.md)
- Host bridges anchor one or more hierarchies in the group; ACPI `_SEG` identifies their Segment Group. Segment Group 0 may omit `_SEG` when it is the only group. [PDF pp. 40, 47](../_source/pages/page-040.md)
- One Segment Group may contain multiple host bridges with distinct, non-overlapping bus ranges and enhanced-configuration base addresses. [PDF pp. 42, 45](../_source/pages/page-042.md)

## Evidence

- [Complete normative glossary entry, PDF p. 9](../_source/pages/page-009.md)
