---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 99
headings: ["5.1.1. PCI Expansion ROM Header Format"]
---

# Source page 99

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  99

Figure 5-1:  PCI Expansion ROM Structure
5.1.1. PCI Expansion ROM Header Format
The information required in each ROM image is split into two different areas.  One area, the ROM
header, is required to be located at the beginning of the ROM image.  The second area, the PCI
Data Structure, must be located in the first 64 KiB of the image.  The format for the PCI Expansion
ROM Header is given below.  The offset is a hexadecimal number from the beginning of the image,
and the length of each field is given in bytes.
Offset Length Value Description
0h 1 55h ROM Signature, byte 1
1h 1 AAh ROM Signature, byte 2
2h-17h 16h xx Reserved (processor architecture unique data)
18h-19h 2 xx Pointer to PCI Data Structure

ROM
Signature
The ROM Signature is a two-byte field containing a 55h in
the first byte and AAh in the second byte.  This signature
must be the first two bytes of the ROM address space for
each image of the ROM.
Pointer to PCI
Data
Structure
The Pointer to the PCI Data Structure is a two-byte pointer
in little-endian format that points to the PCI Data Structure.
The reference point for this pointer is the beginning of the
ROM image.
