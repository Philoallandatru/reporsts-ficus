---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 12
headings: ["2.3.2. Calling Interface for BIOS32 Service Directory"]
---

# Source page 12

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  12
Table 2-1.  Data Structure Fields for the BIOS32 Service Directory
Offset Size Description
0 4 bytes Signature string in ASCII.  The string is "_32_".  This puts an “underscore”
at offset 0, a “3” at offset 1, a “2” at offset 2, and another “underscore” at
offset 3.
4 4 bytes Entry point for the BIOS32 Service Directory.  This is a 32-bit physical
address.
8 1 byte Revision level.  This version has revision level 00h.
9 1 byte Length.  This field provides the length of this data structure in paragraph
(i.e., 16-byte) units.  This data structure is 16 bytes long so this field
contains 01h.
0Ah 1 byte Checksum.  This field is a checksum of the complete data structure.  The
sum of all bytes must add up to 0.
0Bh 5 bytes Reserved.  Must be zero.

Clients of the BIOS32 Service Directory should determine its existence by scanning 0E 0000h to
0F FFF0h looking for the ASCII signature and a valid, checksummed data structure.  If the data
structure is found, the BIOS32 Service Directory can be accessed through the entry point provided
in the data structure.  If the data structure is not found, then the BIOS32 Service Directory (and also
the PCI BIOS) is not supported by the platform.
2.3.2. Calling Interface for BIOS32 Service Directory
The BIOS32 Service Directory is accessed by doing a CALL FAR to the entry point provided in the
Service data structure (see previous section).  There are several requirements about the calling
environment that must be met.  The CS code segment selector and the DS data segment selector
must be set up to encompass the physical page holding the entry point as well as the immediately
following physical page.  They must also have the same base.  Platform BIOS writers must assume
that CS is execute-only and DS is read-only.  The SS stack segment selector must provide at least
1 KiB of stack space.  The calling environment must also allow access to I/O space.
The BIOS32 Service Directory provides a single function to determine whether a particular 32-bit
BIOS service is supported by the platform.  All parameters to the function are passed in registers.
Parameter descriptions are provided below.  If a particular service is implemented in the platform
BIOS, three values are returned.  The first value is the base physical address of the BIOS service.
The second value is the length of the BIOS service.  These two values can be used to build the code
segment selector and data segment selector for accessing the service.  The third value provides the
entry point to the BIOS service encoded as an offset from the base.
