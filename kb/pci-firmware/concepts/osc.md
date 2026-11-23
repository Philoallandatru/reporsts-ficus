---
type: Concept
title: '`_OSC` PCI Host Bridge Negotiation'
description: '`_OSC` is the ACPI object through which OSPM reports feature support
  and requests control of PCI, PCI-X, or PCI Express hierarchy features from platform
  firmware. The PCI host-b...'
tags:
- pci-firmware
- acpi
- uefi
verified:
  by: agent:kb-govern-migrator
  at: '2026-11-23'
status: active
---

# `_OSC` PCI Host Bridge Negotiation

`_OSC` is the ACPI object through which OSPM reports feature support and requests control of PCI, PCI-X, or PCI Express hierarchy features from platform firmware. The PCI host-bridge binding uses UUID `33DB4D5B-1FF7-401C-9657-7441C03DD766` and revision ID 1. [PDF p. 48](../_source/pages/page-048.md)

## Why it matters

The method establishes whether firmware or the operating system may handle native events and configure negotiated capabilities. If a host bridge has no `_OSC`, the operating system must not enable the features defined by this interface because doing so can conflict with firmware. [PDF p. 49](../_source/pages/page-049.md)

## Structure or behavior

The revision-1 Capabilities Buffer contains three DWORDs: the generic ACPI `_OSC` status/error DWORD, a Support Field describing operating-system-supported features, and a Control Field carrying operating-system ownership requests. The operating system ignores modifications to the returned Support Field. [PDF p. 48](../_source/pages/page-048.md)

Firmware returns Control Field bits set for granted features and cleared for denied or unrequested features. A cleared bit means the operating system must not enable that feature; firmware may deny a request only with explicit knowledge that native control would fail because of platform errata or incompatibility. [PDF p. 48](../_source/pages/page-048.md)

Support Field bits covered in this batch report extended PCI Config Operation Region access, ASPM, Clock Power Management, PCI Segment Groups, MSI/MSI-X configuration, OBFF, ASPM Optionality, Error Disconnect Recover, and `_HPX` Type 3 support. [PDF pp. 49-51](../_source/pages/page-049.md)

Control requests covered in this batch include PCI Express and SHPC native hot plug, native PME handling, AER, PCI Express Capability structures, LTR, reliable all-ones error-response handling, DPC configuration, Completion Timeout, and System Firmware Intermediary configuration. Several requests depend on PCI Express Capability Structure control; DPC additionally depends on Error Disconnect Recover support and AER control. [PDF pp. 51-52](../_source/pages/page-051.md)

Granting native hot-plug control requires firmware to route events to device interrupts and then stop updating slot state. Granting PME or AER control similarly transfers the relevant event handling and register ownership; AER control persists across S1-S3 transitions and requires the operating system to preserve configuration when context can be lost. [PDF pp. 53-54](../_source/pages/page-053.md)

Granting PCI Express Capability Structure control transfers configuration and S1-S3 context-preservation responsibility for the PCI Express, Virtual Channel, Power Budgeting, AER, and Serial Number capability structures to the operating system. LTR control similarly transfers LTR configuration and context preservation. [PDF p. 55](../_source/pages/page-055.md)

DPC control transfers the DPC Extended Capability registers to the operating system. When firmware retains DPC, the operating system still has narrowly scoped permission to clear error/status registers during Error Disconnect Recover processing and subsequent device recovery, while firmware is prohibited from racing those writes during the defined windows. [PDF pp. 56-57](../_source/pages/page-056.md)

Completion Timeout control covers the Completion Timeout Value and Disable fields, including their S1-S3 preservation. System Firmware Intermediary control assigns initialization and S1-S3 ownership of the SFI Extended Capability Structure to the operating system. [PDF pp. 57-58](../_source/pages/page-057.md)

## Constraints and edge cases

The binding is required for a host bridge that originates a PCI Express hierarchy and optional for a PCI/PCI-X hierarchy. It applies to the entire hierarchy rooted at that host bridge, whose ACPI identity includes `PNP0A03` or `PNP0A08`. [PDF p. 48](../_source/pages/page-048.md)

Firmware must not deny a control bit merely because it lacks explicit support for a possibly hot-plugged feature. It must assume PCI-X features can exist below a PCI Express hierarchy unless it knows otherwise, while PCI-Express-only control bits must be cleared for a PCI/PCI-X hierarchy. [PDF p. 49](../_source/pages/page-049.md)

For multiple host bridges, the specification recommends consistent capability reporting and negotiation among bridges of the same type; PCI/PCI-X and PCI Express bridges may use different settings. [PDF p. 49](../_source/pages/page-049.md)

With the Query Support Flag set, firmware must not change hardware settings. OSPM should query repeatedly until the returned Capabilities Masked status clears, because a platform may require a supported feature combination before granting a control request. [PDF p. 59](../_source/pages/page-059.md)

Within one boot, support declarations and granted control requests are monotonic: OSPM must preserve them in later calls, firmware cannot revoke a prior grant, and there is no relinquish operation. `_OSC` is evaluated by the hierarchy's main bus driver during relevant native-driver initialization, on host-bridge `Notify(..., 8)`, and after S4 resume. [PDF p. 59](../_source/pages/page-059.md)

Requests for native hot plug, native PME, AER, LTR, DPC, or Completion Timeout require Control Field bit 4 (PCI Express Capability Structure control). DPC also requires AER control, and requesting DPC requires Support Field bit 7 for Error Disconnect Recover; firmware masks an illegally claimed dependent feature. [PDF p. 60](../_source/pages/page-060.md)

## Relationships

- The method is a child of an [ACPI PCI Host Bridge Description](acpi-pci-host-bridge.md) and governs its whole hierarchy. [PDF pp. 48-49](../_source/pages/page-048.md)
- Support Field bit 3 reports operating-system support for [PCI Segment Groups](pci-segment-group.md) and `_SEG`-identified Configuration Space access. [PDF p. 50](../_source/pages/page-050.md)
- Error Disconnect Recover can lead to `_OST` status reporting; `_OST` Arg1 identifies the affected port by Bus, Device, and Function fields. [PDF p. 50](../_source/pages/page-050.md)
- The DPC dependency rules interact with the PCI `_DSM` for DPC Enable and Hot-Plug Surprise Control; when that `_DSM` is available, firmware may clear the hardware Hot-Plug Surprise bit and advertise asynchronous removal through SMBIOS Type 9 instead. [PDF p. 60](../_source/pages/page-060.md)

## Evidence

- [Host-bridge binding and buffer model, PDF p. 48](../_source/pages/page-048.md)
- [Hierarchy-wide negotiation rules, PDF p. 49](../_source/pages/page-049.md)
- [Support Field continuation and `_OST` port identity, PDF p. 50](../_source/pages/page-050.md)
- [Support and requested-control fields, PDF pp. 51-52](../_source/pages/page-051.md)
- [Returned control semantics, PDF pp. 53-54](../_source/pages/page-053.md)
- [Returned control semantics continuation, PDF pp. 55-58](../_source/pages/page-055.md)
- [Evaluation, sequencing, and dependency rules, PDF pp. 59-60](../_source/pages/page-059.md)
- [ASL implementation example, PDF pp. 61-62](../_source/pages/page-061.md)
