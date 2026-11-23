---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 102
headings: ["5.1.3. Device List Format"]
---

# Source page 102

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  102
Pointer to Configuration
Utility Code Header
This pointer is a two-byte pointer in little-endian format that points
to the Expansion ROM’s Configuration Utility Code Header table at
the beginning of the configuration code block described in
Section 5.2.1.24.  The beginning reference point (“offset zero”) for
this pointer is the beginning of the Expansion ROM image.  This
field is only present in Revision 3.0 (and greater) PCI Data structures.
A value of 0000h will be present in this field if the Expansion ROM
does not support a Configuration Utility Code Header. A value of
0000h must be present in this field if the Code Type field contains a
value of 3 (UEFI).
Pointer to DMTF CLP
Entry Point
This pointer is a two-byte pointer in little-endian format that points
to the execution entry point for the DMTP CLP code supported by
this ROM.  The beginning reference point (“offset zero”) for this
pointer is the beginning of the Expansion ROM image.  This field is
only present in Revision 3.0 (and greater) PCI Data structures.  A
value of 0000h will be present in this field if the Expansion ROM
does not support a DMTF CLP code entry point as described in
Section 5.2.1.25. A value of 0000h must be present in this field if the
Code Type field contains a value of 3 (UEFI).

5.1.3. Device List Format
Revision 3.0 (or later) defines a Device List Pointer that points to the list of Device IDs supported
by the Expansion ROM image whose Code Type is not 3 (UEFI).
The beginning reference point (“offset zero”) for this pointer is the beginning of the PCI Data
structure (the first byte of the Signature field).  If this field does not exist (i.e., its contents are zero),
then the Expansion ROM only supports the one specific Device ID listed in the Device ID field in
the PCI Data structure.  However, if this field is non-zero then it must point to a Device List Table.
The format of this table is shown in Table 5-1.
Table 5-1:  Device List Table
Offset Length Description
0 2 Device ID 0 supported
2 2 Device ID 1 supported
4 2 Device ID N supported
N 2 Value of 0000h terminates list
