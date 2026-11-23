---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 38
headings: ["4. PCI Services in ACPI", "4.1. Enhanced Configuration Access Method Base Address"]
---

# Source page 38

PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021 38




4. PCI Services in ACPI
The Advanced Configuration and Power Interface (ACPI) Specification describes a set of common
firmware interfaces that enable robust operating system-directed platform device configuration and
power management of both individual devices and the entire system.  ACPI uses tables to describe
system information, features, and methods for controlling those features.
The following sections provide an overview of ACPI interfaces that are relevant to platforms that
support PCI hierarchies consisting of Conventional PCI, PCI-X, and PCI Express.
4.1. Enhanced Configuration Access Method Base
Address
On PC-compatible systems, the enhanced configuration access mechanism allows PCI configuration
space to be accessed using memory primitives rather than I/O-based primitives (CF8/CFC
mechanism).  For PCI Express and PCI-X Mode 2 hierarchies on these systems, the memory
mapped configuration access mechanism is the only way to access the extended configuration space
(offsets 256-4095).
This section defines an ACPI-based mechanisms to communicate the memory mapped
configuration space base address(es) used for Enhanced Configuration Access Mechanism (defined
in PCI-X and PCI Express Local Bus Specifications) to the operating system:
❑ MCFG:  An ACPI table-based mechanism that is used to communicate the memory mapped
configuration space base addresses corresponding to the (non-hot removable) PCI Segment
Groups and/or base address ranges within a PCI Segment Group available to the system at
boot. The memory mapped configuration space address ranges described exclusively through the
table mechanism are considered to be non-relocatable and non-hot removable for the current
boot.
❑ _CBA:  An ACPI method that is used to report the Enhanced Configuration Access base
address for any PCI Segment Groups and/or base address ranges within a PCI Segment group.
This allows run-time update for the hot added PCI components.
The MCFG table is only used to communicate the base addresses corresponding to the non-hot
removable PCI Segment Groups available to the system at boot.  The _CBA method enables the
system to describe the base address of the memory mapped configuration space for hot plug capable
PCI Segment Groups.
4
