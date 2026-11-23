---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 69
headings: ["4.6.4.1.2. Bus Capabilities Structure Definitions"]
---

# Source page 69

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  69
4.6.4.1.2. Bus Capabilities Structure Definitions
The Bus Capabilities Structures, for different bus types, are discussed in the following table.
Table 4-9:  PCI Bus Capability Structure
Field Byte Length Byte Offset Description
Type 2 0 PCI (Type 1)
Length 2 2 The length of the structure, in bytes, including the
type, starting from offset 0.  This field is used to
record the size of the entire structure.  This field
must return 16.
Attributes 1 4 The bit corresponding to each attribute of the bus
should be set:
01h: 64-bit Device – This bit should be set if the
secondary interface of the bus is 64 bits wide.
02h: PCI-X Mode 1 ECC Capable – This bit
should be set if the bus is capable of supporting
ECC in PCI-X Mode 1.
04h: Device ID Messaging Capable – This bit
should be set if the bridge is capable of forwarding
Device ID Message transactions.
08h: OBFF Capable – This bit should be set if the
OBFF/WAKE# signal is provided to devices
beneath this bridge, but the bridge does not report
support for OBFF in its Device Capabilities 2
register.
Current
Speed/Mode
1 5 Defined encodings are as follows:
0000 0000b – 33 MHz Conventional Mode
0000 0001b – 66 MHz Conventional Mode
0000 0010b – 66 MHz PCI-X with Parity (Mode 1)
0000 0011b – 100 MHz PCI-X with Parity (Mode 1)
0000 0100b – 133 MHz PCI-X with Parity (Mode 1)
0000 0101b – 66 MHz PCI-X with ECC (Mode 1)
0000 0110b – 100 MHz PCI-X with ECC (Mode 1)
0000 0111b – 133 MHz PCI-X with ECC (Mode 1)
0000 1000b – 66 MHz PCI-X 266 (Mode 2)
0000 1001b – 100 MHz PCI-X 266 (Mode 2)
0000 1010b – 133 MHz PCI-X 266 (Mode 2)
0000 1011b – 66 MHz PCI-X 533 (Mode 2)
0000 1100b – 100 MHz PCI-X 533 (Mode 2)
0000 1101b – 133 MHz PCI-X 533 (Mode 2)
0000 1110b to 1111 1110b – Reserved
