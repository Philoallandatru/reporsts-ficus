---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 46
headings: ["4.2. Mechanism for Controlling System Wake From PCI Express", "4.3. PCI Root Bridge Description", "4.3.1. Identification"]
---

# Source page 46

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  46
To retain compatibility with older operating systems that do not recognize the new PNP ID, when
PNP0A08 is used to describe a device in the namespace, it is also required to include PNP0A03 as
the compatible ID (_CID).
Example ASL for PNP0A08 usage:
Device(PCI1) {                // Root PCI Bus
Name(_HID, EISAID("PNP0A08")) // Indicates PCI
Express/PCI-X Mode 2 host hierarchy
Name(_CID, EISAID("PNP0A03")) // To support legacy OS
that does
     // not understand the new HID
 }
Notes regarding use of PNPID and PNP0A08 to indicate PCI Express/PCI-X Mode 2 host bridge
hierarchy:
1. PNP0A08 only indicates support for extended configuration space, that is, each device function
supports 4 KiB of configuration space.  The support for memory mapped configuration access
is indicated by MCFG/_CBA.
2. For PCI-X Mode 2 host bridges, PNP ID of PNP0A08 only indicates that the host bridge is
capable of supporting extended configuration space.  OSPM must call _DSM to identify if the
extended configuration capabilities are currently enabled.
4.2. Mechanism for Controlling System Wake From
PCI Express
An errant PCI Express device may prevent the system from going to sleep by continuously asserting
the PCI Express wake signal.  The PCI Express wake registers, defined in ACPI FADT PM register,
allows OSPM to disable the wake signal to allow the system to enter a sleep state.
Complete details are contained in the ACPI Specification.
4.3. PCI Root Bridge Description
4.3.1. Identification
PCI Host bridge devices in ACPI namespace are identified by PNP ID.  PNP0A03 is used to
indicate PCI/PCI-X host bridge hierarchies.
A PNP ID of PNP0A08 is used to represent PCI Express and PCI-X Mode 2 host bridge
hierarchies to indicate support for extended configuration space.
For further details, see Section 4.1.4.
