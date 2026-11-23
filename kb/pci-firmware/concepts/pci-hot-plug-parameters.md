---
type: Concept
title: PCI Hot-Plug Parameters
description: PCI hot-plug parameters are ACPI objects that provide configuration settings
  for devices inserted into hot-plug slots or devices that firmware did not configure
  at boot. [PDF pp...
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# PCI Hot-Plug Parameters

PCI hot-plug parameters are ACPI objects that provide configuration settings for devices inserted into hot-plug slots or devices that firmware did not configure at boot. [PDF pp. 96-97](../_source/pages/page-096.md)

## Why it matters

They let firmware communicate platform-specific configuration policy down a PCI bus hierarchy while allowing a more capable `_HPX` object to replace legacy `_HPP` settings. [PDF pp. 96-97](../_source/pages/page-096.md)

## Structure or behavior

The optional `_HPP` object supplies cache-line size, latency timer, SERR enable, and PERR enable values. It is placed under the PCI bus where the behavior is required, and its settings inherit through child buses until another `_HPP` is encountered. [PDF pp. 96-97](../_source/pages/page-096.md)

The optional `_HPX` object also provides settings inherited by child buses until overridden. When both `_HPX` and `_HPP` exist, the operating system preferentially evaluates `_HPX`. [PDF p. 97](../_source/pages/page-097.md)

## Constraints and edge cases

For ACPI-managed hot plug, `_PS3` places a device in D3, with device-dependent selection of D3hot or D3cold; `_PS0` brings it back, after which firmware knowledge can be used to determine what context hardware preserved. [PDF p. 97](../_source/pages/page-097.md)

For ACPI-managed online removal, `_EJ0` must leave the device isolated for physical removal when it completes and is recommended to remove slot power when the platform supports that operation. [PDF p. 97](../_source/pages/page-097.md)

## Relationships

- `_HPX` supersedes `_HPP`; both establish inherited bus configuration policy. [PDF p. 97](../_source/pages/page-097.md)
- `_PS3`/`_PS0` govern device power-state transitions, while `_EJ0` governs removal and isolation. [PDF p. 97](../_source/pages/page-097.md)

## Evidence

- [`_HPP` definition, PDF pp. 96-97](../_source/pages/page-096.md)
- [`_HPX`, power state, and removal behavior, PDF p. 97](../_source/pages/page-097.md)
