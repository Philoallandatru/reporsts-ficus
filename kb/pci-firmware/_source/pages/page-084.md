---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 84
headings: []
---

# Source page 84

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  84
Return: Downstream Port Containment Status from firmware
Type: Integer
Description:
0: The status of the operation is success. DPC is disabled and the Hot-Plug Surprise bit may be
set to 1 for hot-plug surprise capable ports.
1: The status of the operation is success. DPC is enabled and the Hot-Plug Surprise bit may be
cleared to 0 for hot-plug surprise capable ports.
2: The status of the operation is failure. DPC and Hot-Plug Surprise state are not specified.
