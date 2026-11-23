---
type: Concept
title: PERST# Assertion Delay
description: PCI `_DSM` Function `0Bh` requests a fixed delay between receipt of `PME_TO_Ack`
  at the Downstream Port that sent `PME_Turn_Off` and assertion of `PERST#` during
  the correspondi...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PERST# Assertion Delay

PCI `_DSM` Function `0Bh` requests a fixed delay between receipt of `PME_TO_Ack` at the Downstream Port that sent `PME_Turn_Off` and assertion of `PERST#` during the corresponding device transition to D3cold in S0. [PDF p. 81](../_source/pages/page-081.md)

## Why it matters

Because `PERST#` may indicate imminent power removal and no delay after its assertion is guaranteed, this function gives the device a bounded preparation interval before reset assertion. [PDF p. 81](../_source/pages/page-081.md)

## Structure or behavior

The function uses lowest valid Revision ID 4, Function Index `0Bh`, and an integer Arg3 delay in microseconds, capped at 10 ms. A successful call returns Arg3; a failed call returns the most recent successful value, or 0 when none exists. [PDF p. 81](../_source/pages/page-081.md)

Once accepted, the delay applies to every applicable D3cold transition. Repeated calls may change the value for the next transition. [PDF p. 81](../_source/pages/page-081.md)

## Constraints and edge cases

The method is valid only in the scope of a PCI Express Downstream Port terminated by an add-in slot or connector. Software aggregates child requests below the port by requesting their maximum delay. [PDF p. 81](../_source/pages/page-081.md)

The delay applies to D3cold transitions in S0, not transitions from S0 into S3, S4, or S5. It does not guarantee any interval between `PERST#` assertion and power removal; wake-required auxiliary rails remain powered when a function is armed for wake. [PDF p. 81](../_source/pages/page-081.md)

## Relationships

- This is Function `0Bh` in the [PCI Device Specific Method (`_DSM`)](pci-dsm.md) namespace. [PDF p. 81](../_source/pages/page-081.md)
- It supplements device power-transition timing rather than the first-access delays described by [PCI Device Readiness Timing](pci-device-readiness-timing.md). [PDF pp. 78, 81](../_source/pages/page-078.md)

## Evidence

- [Timing purpose, scope, arguments, and return behavior, PDF p. 81](../_source/pages/page-081.md)
