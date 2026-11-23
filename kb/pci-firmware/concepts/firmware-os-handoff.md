---
type: Concept
title: Firmware/Operating System Handoff
description: 'Firmware/Operating System Handoff is the ownership boundary at the return
  from UEFI `ExitBootServices()`: firmware owns the PCI subsystem before the call
  returns, and the operat...'
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# Firmware/Operating System Handoff

Firmware/Operating System Handoff is the ownership boundary at the return from UEFI `ExitBootServices()`: firmware owns the PCI subsystem before the call returns, and the operating system owns it afterward. [PDF p. 34](../_source/pages/page-034.md)

## Why it matters

Firmware is required to leave enough of the hierarchy configured to boot and provide console interaction, but the operating system cannot assume that every PCI device or bridge was configured. [PDF pp. 34-36](../_source/pages/page-034.md)

## Structure or behavior

Firmware must configure the full chipset, bridge, and multifunction-device path to boot and console devices, and it must configure every Host Bridge. Other devices and PCI-to-PCI bridges may remain unconfigured. [PDF pp. 34-35](../_source/pages/page-034.md)

For a device BAR, the operating system determines firmware configuration from the corresponding I/O Enable, Memory Enable, or Expansion ROM BAR enable bit; Bus Master Enable does not establish BAR validity. An enabled range must be correctly configured and respond even if the device cannot master transactions. [PDF p. 34](../_source/pages/page-034.md)

Firmware must deassert `RST#` for occupied PCI slots below a Host Bridge and observe required reset-to-configuration-access delays before handoff. PCI-to-PCI secondary buses unused by boot or console devices may remain in reset. [PDF p. 36](../_source/pages/page-036.md)

The operating system must keep device resources within the parent Host Bridge `_CRS` windows and account for `_TRA`, `_TTP`, and `_TRS` translation after its ACPI interpreter is available. Before re-enabling a resource, it must program a non-conflicting BAR value within the reported range. [PDF pp. 36-37](../_source/pages/page-036.md)

## Constraints and edge cases

UEFI drivers and applications must not change BAR assignments or PCI-to-PCI bridge configuration owned by the firmware bus-configuring component. The operating system is responsible for hot-plug configuration, unusually slow reset recovery, and bridges deeper than firmware supports. [PDF pp. 34-36](../_source/pages/page-034.md)

The Expansion ROM BAR is normally disabled and its content treated as invalid at handoff. Device-independent software must not assume independent ROM and normal BAR decoders; it must disable the Expansion ROM BAR before accessing other BARs unless it has device-specific knowledge of dual decoders. [PDF p. 37](../_source/pages/page-037.md)

## Relationships

- Transfers ownership from [UEFI PCI Services](uefi-pci-services.md) to operating-system PCI and ACPI services.
- Uses ACPI Host Bridge resource and translation descriptions to constrain later [Configuration Space](configuration-space.md) programming. [PDF pp. 35-37](../_source/pages/page-035.md)

## Evidence

- [Ownership boundary and device-configuration scope, PDF p. 34](../_source/pages/page-034.md)
- [Host Bridge and PCI-to-PCI bridge requirements, PDF p. 35](../_source/pages/page-035.md)
- [Reset, BAR ownership, and translation rules, PDF p. 36](../_source/pages/page-036.md)
- [Host Bridge range and Expansion ROM BAR rules, PDF p. 37](../_source/pages/page-037.md)

