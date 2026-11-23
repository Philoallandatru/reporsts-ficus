---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 41
headings: []
---

# Source page 41

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  41
Table 4-2:  MCFG Table to Support Enhanced Configuration Space Access
Field Byte
Length
Byte
Offset
Description
Header
    Signature 4 0 “MCFG”.  Signature for the Memory mapped
configuration space base address Description
Table.  (refer to Note 1)
    Length 4 4 Length, in bytes, of the entire MCFG Description
table including the memory mapped configuration
space base address allocation structures.
    Revision 1 8 1
    Checksum 1 9 Entire table must sum to zero
    OEMID 6 10 OEM ID
    OEM Table ID 8 16 For the MCFG Description Table, the table ID is
the manufacture model ID
    OEM Revision 4 24 OEM revision of MCFG table for supplied OEM
Table ID
    Creator ID 4 28 Vendor ID of utility that created the table
    Creator Revision 4 32 Revision of utility that created the table
    Reserved 8 36 Reserved
Configuration space
base address
allocation structure [n]
--- 44 A list of the memory mapped configuration base
address allocation structures.  This list will
contain at least one entry corresponding to each
PCI Segment Group present in the platform.  The
structure of this entry is defined in Table 4-3.
Notes:
1. A table signature “MCFG” is reserved for this purpose and the header for the table is shown in Table 4-2.
Based on the signature and table revision, the operating system can then interpret the implementation-
specific data within the table. The Table Revision for revision 1.0 of the MCFG table is set to 1.
2. If the operating system does not natively comprehend reserving the MMCFG region, the MMCFG region
must be reserved by firmware.  The address range reported in the MCFG table or by _CBA method (see
Section 4.1.3) must be reserved by declaring a motherboard resource.  For most systems, the motherboard
resource would appear at the root of the ACPI namespace (under \_SB) in a node with a _HID of EISAID
(PNP0C02), and the resources in this case should not be claimed in the root PCI bus’s _CRS.  The
resources can optionally be returned in Int15 E820h or EFIGetMemoryMap as reserved memory but must
always be reported through ACPI as a motherboard resource.
3. This table must not include the memory mapped configuration base addresses for hot pluggable PCI
Segment Groups.  Such PCI Segment Groups must be described by using the _CBA method (see
Section 4.1.3) in the corresponding ACPI namespace object.
