---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 70
headings: []
---

# Source page 70

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  70
Field Byte Length Byte Offset Description
Supported
Speeds/Modes
2 6 The bit corresponding to each supported bus
speed/mode should be set:
Bit[5:0]
00 0001b: Conventional PCI 33 MHz
00 0010b: Conventional PCI 66 MHz
00 0100b: PCI-X 66 MHz
00 1000b: PCI-X 133 MHz
01 0000b: PCI-X 266 MHz
10 0000b: PCI-X 533 MHz
Bit[15:6] Reserved
Voltage 1 8 0:  3.3 V
1:  5 V
2+:  Reserved
Reserved 7 9 0
