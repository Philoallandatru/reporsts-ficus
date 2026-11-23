---
type: Concept
title: D3cold Auxiliary Power Limit
description: PCI `_DSM` Function `0Ah` lets a device driver request an auxiliary-power
  budget for D3cold and lets platform firmware grant, deny, defer, or avoid main-power
  removal. [PDF pp....
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# D3cold Auxiliary Power Limit

PCI `_DSM` Function `0Ah` lets a device driver request an auxiliary-power budget for D3cold and lets platform firmware grant, deny, defer, or avoid main-power removal. [PDF pp. 79-80](../_source/pages/page-079.md)

## Why it matters

The negotiation prevents a device from drawing more auxiliary power than the platform can supply after main power is removed. A granted request replaces earlier limits; any other result leaves earlier grants and applicable form-factor or PCI Express requirements unchanged. [PDF p. 79](../_source/pages/page-079.md)

## Structure or behavior

The function uses lowest valid Revision ID 4, Function Index `0Ah`, and an integer Arg3 measured in mW. Arg3 ranges from 0 through the form-factor limit; `8000 0000h` requests that main power not be removed in D3cold while the system is in S0. [PDF p. 79](../_source/pages/page-079.md)

Return `0h` denies the request, `1h` grants the requested auxiliary power, and `2h` promises no main-power removal in S0. Values `11h`–`1Fh` ask software to retry after 1–15 seconds, encoded in the low four bits. [PDF p. 80](../_source/pages/page-080.md)

## Constraints and edge cases

The method is valid only in the scope of a PCI Express Downstream Port. Software aggregates child-device requests beneath that port; Function 0 of a Multi-Function Device reports the aggregate requirement of all its functions. A device may call repeatedly to discover availability, retry, or change its requirement. [PDF p. 79](../_source/pages/page-079.md)

Firmware may return a retry value only once per `_DSM` instance unless another call arrives before the earlier interval expires. Firmware must not grant more power than the platform budget, and a device must not exceed the negotiated value after entering D3cold. [PDF pp. 79-80](../_source/pages/page-079.md)

## Relationships

- This is Function `0Ah` in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF p. 79](../_source/pages/page-079.md)
- It coordinates D3cold auxiliary power separately from the main-power-removal decision represented by return `2h` or Arg3 `8000 0000h`. [PDF pp. 79-80](../_source/pages/page-079.md)

## Evidence

- [Request, placement, and arguments, PDF p. 79](../_source/pages/page-079.md)
- [Return codes and platform budgeting, PDF p. 80](../_source/pages/page-080.md)
