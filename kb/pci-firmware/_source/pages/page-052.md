---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 52
headings: []
---

# Source page 52

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  52
Control Field
Bit Offset Interpretation
4 PCI Express Capability Structure control
The operating system sets this bit to 1 to request control over the PCI Express
Capability structures (standard and extended) defined in the PCI Express Base
Specification, Revision 1.1.  These capability structures are the PCI Express
Capability, the Virtual Channel Extended Capability (Capability ID 002, not ID
009), the Power Budgeting Extended Capability, and the Device Serial Number
Extended Capability structures.
5 Latency Tolerance Reporting control
The operating system sets this bit to 1 to request control over PCI Express
Latency Tolerance Reporting.
If the operating system sets this bit, it must also set bit 4, PCI Express Capability
Structure control, to request control of the PCI Express Capability tructure.
6 The operating system sets this bit to 1 to indicate that all certified IO drivers will
never interpret as valid data an all 1’s response to a read from a Function’s
Memory Mapped IO space (MMIO BAR memory), IO space, or Configuration
space.  An all 1’s read response is returned by hardware to indicate certain error
conditions including surprise removal of a PCIe device, and reliable detection of
those error cases requires that an all 1’s response must never be interpreted as
valid by an IO driver.
7 PCI Express Downstream Port Containment Configuration Control
The operating system sets this bit to 1 to request control over PCI Express
Downstream Port Containment configuration.
If the operating system sets this bit, it must also set bit 7 of the Support field
(indicating support for Error Disconnect Recover notifications) and bits 3 and 4 of
the Control field (requesting control of PCI Express Advanced Error Reporting and
the PCI Express Capability Structure).
8 PCI Express Completion Timeout Control
The operating system sets this bit to 1 to request control over the PCI Express
Completion Timeout fields.
If the operating system sets this bit, it must also set bit 4, PCI Express Capability
Structure control, to request control of the PCI Express Capability Structure.
9 PCI Express System Firmware Intermediary Configuration Control
The operating system sets this bit to 1 to request control over configuration of PCI
Express System Firmware Intermediary (SFI).
SFI is architected primarily for use by system firmware. In a few cases like
embedded systems, it may make sense for the operating system to own SFI
instead. It is recommended that general-purpose operating systems never request
ownership, and that general-purpose platforms never grant ownership to an
operating system if requested.
10 - 31 Reserved
