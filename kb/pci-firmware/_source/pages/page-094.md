---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 94
headings: ["4.7.5. Set PCIe SSD Status LED States (Function Index 3)"]
---

# Source page 94

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  94
4.7.5. Set PCIe SSD Status LED States (Function Index 3)
This function returns the PCIe SSD Status LED State. OSPM should call this method after it calls
the query method of this _DSM. This function must return success if it is called with no bit set.
Table 4-17 lists the Input (Arg3) field description. Table 4-18 lists the Output Buffer for Function
Index 3.  Table 4-19 lists the Function-specific Error Codes for Function Index 3.
Table 4-17: Input (Arg3)
Field Byte Length Byte Offset Description
PCIe SSD Status
LED State
4 0 Table 4-15 has a detail description of each bit:
Bit [0] – Reserved
Bit [1] – Reserved
Bit [2] – OK
Bit [3] – Locate
Bit [4] – Fail
Bit [5] – Rebuild
Bit [6] – PFA
Bit [7] - Hot Spare
Bit [8] –Critical Array Control
Bit [9] –Failed Array Control
Bit [10] – Invalid Device
Bit [11] – Disabled
Bit [12-31] – Reserved

Table 4-18: Output Buffer for Function Index 3
Field Byte Length Byte Offset Description
Status 4 0 See Table 4-13
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
Bit [7] - Hot Spare
Bit [8] –Critical Array Status
Bit [9] –Failed Array Status
Bit [10] – Invalid Device
Bit [11] – Disabled
Bit [12-31] – Reserved
