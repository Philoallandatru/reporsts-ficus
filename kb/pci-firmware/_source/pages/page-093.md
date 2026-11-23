---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 93
headings: ["4.7.4. Get PCIe SSD Status LED States (Function Index 2)"]
---

# Source page 93

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  93
4.7.4. Get PCIe SSD Status LED States (Function Index 2)
This function returns the PCIe SSD Status LED State. See Table 4-16 for Output Buffer for
Function Index 2 descriptions.
Input (Arg3)
None
Table 4-16: Output Buffer for Function Index 2
Field Byte Length Byte Offset Description
Status  4 0 See Table 4-13
PCIe SSD Status
LED State
4 4 Table 4-15 has a detail description of each bit:
Bit [0] – Reserved
Bit [1] – Reserved
Bit [2] – OK
Bit [3] – Locate
Bit [4] – Fail
Bit [5] – Rebuild
Bit [6] – PFA
Bit [7] – Hot Spare
Bit [8] – In Critical Array Status
Bit [9] – In Failed Array Status
Bit [10] – Invalid Device
Bit [11] – Disabled
Bit [12-31] – Reserved
