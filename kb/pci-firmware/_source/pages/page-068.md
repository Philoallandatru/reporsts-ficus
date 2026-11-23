---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 68
headings: ["4.6.4. _DSM for PCI Bus Capabilities", "4.6.4.1. Bus Capabilities Structure", "4.6.4.1.1. Bus Types"]
---

# Source page 68

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  68
4.6.4. _DSM for PCI Bus Capabilities
This section defines a mechanism for a PCI root bus to report its capabilities and operating mode to
software.  PCI buses that are created by PCI to PCI bridges already report this information through
hardware registers in the configuration space header, PCI-X capability and/or SHPC capability.
Since root buses are exposed through ACPI, no such hardware registers exist, and this information
must be described in a different manner.
The _DSM method, defined in the ACPI Specification, is used to provide the information about the
capabilities of a root bus.  The UUID used for the bus capabilities information and the structure of
the buffer returned is described below.
Note:  SMBIOS has type 9 entry reporting slot information, but the interface is static with no
dynamic update capability.  The entry has not been updated to reflect the most current technologies.
The _DSM mechanism replaces the SMBIOS interface.
4.6.4.1. Bus Capabilities Structure
This section defines the concept of Bus Capabilities Structure.  This structure describes the different
attributes of a root bus.  The Bus Capabilities Structure is bus-type specific and is returned by the
_DSM defined here.  A root bus can only have a single Bus Capability Structure.
The Bus Capabilities Structure must be aligned to a 4-byte boundary to ensure that future structure
definitions do not cause any alignment issues for the consumer of these structures.
4.6.4.1.1. Bus Types
Table 4-8 describes the different bus types that can be used in the type field of the Bus Capabilities
Structures.  The type field is 2 bytes in size.
Table 4-8:  Bus Types
Type Description
0 Reserved
1 PCI
2+ Reserved
