---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 45
headings: ["4.1.5. Plug-and-Play ID Defined for Enhanced Configuration Space Access Capable Devices"]
---

# Source page 45

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  45


IMPLEMENTATION NOTE
Multiple Host Bridges
A platform may have multiple PCI Express or PCI-X host bridges.  The base address for the
MMCONFIG space for these host bridges may need to be allocated at different locations.
Historically, in such cases, using MCFG table and _CBA method as defined in this section means
that each of these host bridges must be in its own PCI Segment Group. This approach is referred
to as the legacy interpretation of this specification. A newer interpretation of this specification allows
“multiple host bridges with base addresses allocated at different locations” to exist within the same
PCI Segment Group. Vendors who choose to implement to the newer interpretation bear the
responsibility that supported operating systems can handle the newer interpretation.
Allocating base addresses to non-contiguous regions of memory has been achievable in some
implementations with an address mapping feature to make non-contiguous regions of memory
appear to be contiguous to the operating system. The newer interpretation removes the need for
such an address mapping feature thereby simplifying implementations.
Allocating base addresses to non-contiguous regions of memory has also been possible using the
legacy interpretation of the specification by employing different PCI Segment Group Numbers.
However, the newer interpretation of the specification preserves the use of a single PCI Segment
Group Number since implementations will not allow peer-to-peer communications across multiple
PCI Segment Groups.
For example, the Base Address field value returned by MCFG of a bus number range starting at
0xE2000000, where the Start Bus Number is 0, would be 0xE2000000. The Base Address field
value returned by MCFG of a bus number range starting at 0xE2000000, where the Start Bus
Number is 0x40, would be (0xE20000000 – (0x40 << 20)) or 0xDE000000. Therefore, the lowest
possible Base Address field value returned by MCFG is a function of Start Bus Number:
Base Address=(Start of memory mapped configuration address range)-((0x100000)*(Start Bus Number)).
If this platform also needs to support legacy operating systems or x86 BIOS Option ROMs, the
CF8/CFCh access mechanism (which is PCI Segment Group unaware and only can support up to
256 bus numbers) must also be supported.  There may be a number of implementation choices to
make these two work together; for example, the bus numbers in each of the PCI Segment Group
can be made to not overlap.  This would make the CF8/CFCh access still appear to be Segment
Group unaware and support up to 256 buses while using the MCFG/_CBA definition to describe
host bridges MMCONFIG base addresses that are allocated at different locations.
Note that in this arrangement, even though the PCI Segment Group concept is used, the total
number of PCI buses is still limited to 256 due to the CF8/CFCh limitation.
4.1.5. Plug-and-Play ID Defined for Enhanced
Configuration Space Access Capable Devices
Currently, a Plug-and-Play ID (PNP ID) of PNP0A03 is used to indicate host-PCI bridge devices in
ACPI namespace.  This PNP ID is used to describe both PCI/PCI-X hierarchies.
A new PNP ID of PNP0A08 is defined to indicate PCI Express as well as PCI-X Mode 2 host
bridges to the operating system.  The unique ID for these host bridges will allow the host to
distinguish a PCI Express, PCI-X Mode 2 hierarchy in a mixed host-bridge environment and also
allow the operating system to tune the driver loading process to the capabilities of the underlying
I/O hierarchy.
