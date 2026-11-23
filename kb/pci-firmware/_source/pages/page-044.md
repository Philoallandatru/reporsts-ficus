---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 44
headings: ["4.1.4. System Software Implication of MCFG and _CBA"]
---

# Source page 44

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  44
Example ASL for _CBA usage:
Scope(\_SB) {
      …
Device(PCI1) {                // Root PCI Bus
Name(_HID, EISAID("PNP0A03")) // Need _HID for root device
Name(_SEG, 1)    // PCI Segment Group 1
Method (_CRS, ResourceTemplate()
{
 …
}
Method(_CBA, 0) {
// Bits 63:0 of the base address
Return (0xE000000000000000)
} // end of _CBA method
} // end PCI1
} // end scope SB
4.1.4. System Software Implication of MCFG and _CBA
The base address returned by MCFG table for a given bus number range is always with respect to
bus 0 of that particular bus number range as specified in the PCI Express Base Specification (and the
PCI-X Specification).  It is the responsibility of system software to calculate the start and end of the
supported memory mapped configuration address range based on the start and end bus numbers
specified in the MCFG entry.  System software must make no assumptions about the memory range
corresponding to the base address up to the start of the memory mapped configuration space (as
specified by start bus number).
The base address returned by _CBA for a given PCI Segment Group is always with respect to bus 0
as specified in the PCI Express Base Specification (and the PCI-X Specification).  It is the responsibility of
system software to calculate the start and end of the supported memory mapped configuration
address range for the host bridge based on the bus range supported by the host bridge as identified
by _CRS.
