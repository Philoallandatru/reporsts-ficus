---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 42
headings: []
---

# Source page 42

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  42
The structure in Table 4-3 describes the association between the PCI Segment Group and the
corresponding memory mapped configuration base address.  This table describes the details of this
structure.
Table 4-3:  Memory Mapped Enhanced Configuration Space Base Address Allocation
Structure
Field Byte
Length
Byte
Offset
Description
Base Address  8 0 Processor-relative Base Address for the
Enhanced Configuration Access Mechanism
PCI Segment Group
Number
2 8 PCI Segment Group Number. Default is 0.  For
all other PCI Segment Groups, this field value
should correspond to the value returned by _SEG
object in ACPI namespace for the applicable host
bridge device.
Start Bus Number 1 10 Start PCI Bus number decoded by the host
bridge
End Bus Number 1 11 End PCI Bus number decoded by the host bridge
Reserved 4 12 Reserved

The MCFG table format allows for more than one memory mapped base address entry (instance of
Table 4-3) provided each entry (memory mapped configuration space base address allocation
structure) corresponds to a unique PCI Segment Group consisting of 256 PCI buses.  Multiple
entries corresponding to a single PCI Segment Group are also allowed provided the Field (PCI
Segment Group Number, Start Bus Number, and End Bus Number) uniquely identifies each PCI
Host Bridge and the bus number values do not overlap.
❑ The PCI Segment Group Number field denotes the PCI Segment Group corresponding to the
base address field in the structure.  For systems supporting multiple PCI Segment Groups, this
field should correspond to the value returned by _SEG object in ACPI namespace for the
applicable host bridge device.  If the system only contains a single (default) PCI Segment Group,
namely, PCI Segment Group 0, no corresponding _SEG object is required.
❑ The base address field provides the 64-bit physical address of the base of the  memory mapped
configuration space associated with the PCI Segment Group.  It is the responsibility of the
provider of the table to ensure that the base address reported is consistent with the requirements
for the hardware implementation.  For PCI-X and PCI Express platforms utilizing the enhanced
configuration access method, the base address of the memory mapped configuration space
always corresponds to bus number 0 (regardless of the start bus number decoded by the host
bridge) and further must comply with alignment requirements of the corresponding local bus
specification.  The unsupported upper bits of the physical address must be set to 0.
