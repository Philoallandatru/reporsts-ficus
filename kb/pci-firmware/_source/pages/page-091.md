---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 91
headings: ["4.7.3. Get PCIe SSD Supported LED States"]
---

# Source page 91

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  91
4.7.3. Get PCIe SSD Supported LED States
This function returns the supported LED states that OSPM can control. See Table 4-14 for Output
Buffer descriptions.
Input (Arg3)
None
Table 4-14: Output Buffer
Field Byte Length Byte Offset Description
Status  4 0 See Table 4-13
PCIe SSD Status
LED State
4 4 Table 4-15 has a detail description of the different
LED states:
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
Bit [2] thru Bit [11] indicate support for different LED states. Table 4-15 provides a detailed description
of each state. If the bit is set, then OSPM controls the state.
