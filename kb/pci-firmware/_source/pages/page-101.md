---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 101
headings: []
---

# Source page 101

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  101
PCI Data Structure Length The PCI Data Structure Length is a 16-bit field that defines the
length of the data structure from the start of the data structure (the
first byte of the Signature field).  This field is in little-endian format
and is in units of bytes.
PCI Data Structure
Revision
The PCI Data Structure Revision field is an eight-bit field that
identifies the data structure revision level.  The revision level is 3 for
the current specification.
Class Code The Class Code field is a 24-bit field with the same fields and
definition as the class code field in the Configuration Space for this
device.
Image Length The Image Length field is a two-byte field that represents the length
of the image.  This field is in little-endian format, and the value is in
units of 512 bytes.
Revision Level The Revision Level field is a two-byte field that contains the revision
level of the Vendor’s code in the ROM image.
Code Type The Code Type field is a one-byte field that identifies the type of
code contained in this section of the ROM.  The code may be
executable binary for a specific processor and system architecture or
interpretive code.  The following code types are assigned:
Type Description
0  Intel x86, PC-AT compatible
1  Open Firmware standard for PCI9
2  Hewlett-Packard PA RISC
3  Unified Extensible Firmware Interface (UEFI)
4-FFh Reserved
Last Image Indicator Bit 7 in this field tells whether or not this is the last image in the
ROM.  A value of 1 indicates “last image;” a value of 0 indicates that
another image follows.  Bits 0-6 are reserved.
Maximum Run-Time
Image Length
The Image Length field is a two-byte field that represents the
maximum length of the image after the initialization code has been
executed.  This field is in little-endian format, and the value is in units
of 512 bytes.  This field will be used to determine if the run-time
image size is small enough to fit in the memory remaining in the
system.  This field is only present in Revision 3.0 and later of the PCI
Data structure.

9 Open Firmware is a processor architecture and system architecture independent standard for dealing with device
specific option ROM code.  Documentation for Open Firmware is available in the IEEE 1275-1994 Standard for Boot
(Initialization, Configuration) Firmware Core Requirements and Practices.  A related document, PCI Bus Binding to
IEEE 1275-1994, specifies the application of Open Firmware to the PCI local bus, including PCI-specific requirements
and practices.  This document may be obtained using anonymous FTP to the machine playground.sun.com with the
filename /pub/p1275/bindings/postscript/PCI.ps.
