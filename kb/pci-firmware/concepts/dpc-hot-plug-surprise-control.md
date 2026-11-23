---
type: Concept
title: DPC and Hot-Plug Surprise Control
description: PCI `_DSM` Function `0Ch` coordinates Downstream Port Containment (DPC)
  enablement with suppression of the Hot-Plug Surprise capability for a DPC-capable
  Root Port or Switch Dow...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# DPC and Hot-Plug Surprise Control

PCI `_DSM` Function `0Ch` coordinates Downstream Port Containment (DPC) enablement with suppression of the Hot-Plug Surprise capability for a DPC-capable Root Port or Switch Downstream Port. [PDF pp. 82-84](../_source/pages/page-082.md)

## Why it matters

DPC and Hot-Plug Surprise must change in a safe order: leaving Hot-Plug Surprise suppressed while DPC is disabled creates a window where a Surprise Down error may escape containment and become an uncorrectable error. [PDF p. 82](../_source/pages/page-082.md)

## Structure or behavior

Function `0Ch` takes a one-integer package: 0 requests DPC disabled and 1 requests DPC enabled. Firmware changes DPC itself when it owns DPC; when the operating system owns DPC, the operating system disables it after the call or enables it before the call. Firmware coordinates the Hot-Plug Surprise bit or the SFI HPS Suppress bit around that ownership-dependent step. [PDF p. 83](../_source/pages/page-083.md)

The return is 0 for successful disabled state, 1 for successful enabled state, and 2 for failure with unspecified DPC and Hot-Plug Surprise state. Enabling is mandatory when the function is implemented, though firmware may refuse a particular enable request; disabling support is optional. [PDF pp. 83-84](../_source/pages/page-083.md)

## Constraints and edge cases

The current definition uses Revision ID 6, while the lowest valid Revision ID is 5 because the earlier definition came from the DPC Related Enhancements ECN. The method may appear on a DPC-capable Root Port or Switch Downstream Port, and firmware may apply its setting to downstream ports without their own instance. [PDF pp. 82-83](../_source/pages/page-082.md)

An Error Disconnect Recovery-aware operating system must evaluate the function after `_OSC`, regardless of DPC ownership, and must not evaluate it while the port is DPC-triggered. Firmware implementing Error Disconnect Recovery on a port must provide this function there. [PDF p. 82](../_source/pages/page-082.md)

The event-recovery flow can involve firmware and operating-system interrupt handlers in either execution order. A port deliberately left DPC-triggered or link-disabled after a persistent error must be released when a hot-plug device is removed so a later insertion can operate. [PDF pp. 85-86](../_source/pages/page-085.md)

## Relationships

- This is Function `0Ch` in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace and follows DPC ownership negotiated through [`_OSC`](osc.md). [PDF pp. 60, 82](../_source/pages/page-060.md)
- Function `0Dh`, introduced on the neighboring page, can identify the child port that actually experienced containment when Error Disconnect Recovery notification targets a parent port. [PDF p. 87](../_source/pages/page-087.md)
- `_OST` reports Error Disconnect Recovery results back to firmware; the sample flow uses status values `80h` and `81h` with the affected BDF encoded in Arg1. [PDF pp. 85-87](../_source/pages/page-085.md)

## Evidence

- [Ownership, sequencing, and placement, PDF p. 82](../_source/pages/page-082.md)
- [Arguments and enable/disable procedure, PDF p. 83](../_source/pages/page-083.md)
- [Return status, PDF p. 84](../_source/pages/page-084.md)
- [Recovery flow and concurrency notes, PDF pp. 85-86](../_source/pages/page-085.md)
