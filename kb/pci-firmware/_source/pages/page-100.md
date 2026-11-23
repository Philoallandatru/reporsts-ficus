---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 100
headings: ["5.1.2. PCI Data Structure Format"]
---

# Source page 100

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  100
5.1.2. PCI Data Structure Format
The PCI Data Structure must be located within the first 64 KiB of the ROM image and must be
DWORD aligned.  The PCI Data Structure contains the following information:
Offset Length Description
0 4 Signature, the string “PCIR"
4h 2 Vendor Identification
6h 2 Device Identification
8h 2 Device List Pointer
Ah 2 PCI Data Structure Length
Ch 1 PCI Data Structure Revision
Dh 3 Class Code
10h 2 Image Length
12h 2 Revision Level of the Vendor’s ROM
14h 1 Code Type
15h 1 Last Image Indicator
16h 2 Maximum Run-time Image Length
18h 2 Pointer to Configuration Utility Code
Header
1Ah 2 Pointer to DMTF CLP Entry Point

Signature These four bytes provide a unique signature for the PCI Data
Structure.  The string “PCIR” is the signature with “P” being at
offset 0, “C” at offset 1, etc.
Vendor Identification The Vendor Identification field is a 16-bit field with the same
definition as the Vendor Identification field in the Configuration
Space for this device.
Device Identification The Device Identification field is a 16-bit field with the same
definition as the Device Identification field in the Configuration
Space for this device.
Device List Pointer The Device List Pointer is a two-byte pointer in little-endian format
that points to the list of Device IDs supported by this ROM.  The
beginning reference point (“offset zero”) for this pointer is the
beginning of the PCI Data structure (the first byte of the Signature
field).  This field is only present in Revision 3.0 (and greater) PCI
Data structures. A value of 0000h will be present in this field if the
Expansion ROM does not support Device List. A value of 0000h
must be present in this field if the Code Type field contains a value
of 3 (UEFI).
