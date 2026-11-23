---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 50
headings: []
---

# Source page 50

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  50
Support Field
Bit Offset
Interpretation
3 PCI Segment Groups supported
The operating system sets this bit to 1 if it supports PCI Segment Groups as
defined by the _SEG object and access to the configuration space of devices in
PCI Segment Groups as described by this specification. Otherwise, the operating
system sets this bit to 0.
4 MSI supported
The operating system sets this bit to 1 if it supports configuration of devices to
generate message-signaled interrupts, either through the MSI Capability or the
MSI-X Capability.  Otherwise, the operating system sets this bit to 0.
5 Optimized Buffer Flush and Fill supported
The operating system sets this bit to 1 if it supports the OBFF feature and will
enable this feature during a native hot plug insertion event if supported by the
newly added device in a hierarchy where OBFF is supported.  Otherwise, the
operating system sets this bit to 0.
6 ASPM Optionality supported
The operating system sets this bit to 1 if it properly recognizes and manages
ASPM support on PCI Express components which report support for ASPM L1
only in the ASPM Support field within the Link Capabilities Register.  Otherwise,
the operating system sets this bit to 0.
7 Error Disconnect Recover Supported
The operating system sets this bit to 1 if it supports Error Disconnect Recover
notification on PCI Express Host Bridges, Root Ports and Switch Downstream
Ports. Otherwise, the operating system sets this bit to 0. Refer to the ACPI
Specification for more information.
In the context of PCIe, support for Error Disconnect Recover implies that the
operating system will invalidate the software state associated with child devices of
the port without attempting to access the child device hardware. If the operating
system supports Downstream Port Containment (DPC), as indicated by the
operating system setting bit 7 of _OSC control field, the operating system shall
attempt to recover the child devices if the port implements the Downstream Port
Containment Extended Capability. If the operating system continues operation, the
operating system must inform the Firmware of the status of the recovery operation
via the _OST method. The operating system shall invoke _OST on the same ACPI
Device where the Error Disconnect Recover notification was received. The upper
word of Arg1 argument of _OST carries the Bus, Device, and Function number of
the port that experienced the containment event. The segment number of this port
is equal to the segment number of the Error Disconnect Recover notification target.
The layout of Arg1 is as follows:
Bit Position Definition
15:0 Status of the operation (Refer to the ACPI Specification).
18:16 Function number of the port that experienced the containment
event
23:19 Device number of the port that experienced the containment event
31:24 Bus number of the port that experienced the containment event
