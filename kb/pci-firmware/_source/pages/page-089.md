---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 89
headings: ["4.7. _DSM Definitions for PCIe SSD Status LED"]
---

# Source page 89

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  89
4.7. _DSM Definitions for PCIe SSD Status LED
_DSM (Device Specific Method) is defined in the ACPI Specification. The _DSM method defined in
this section is required to be under the ACPI object representing the embedded PCIe
device/function or under the ACPI PCIe description representing the add-in PCI Express slot. The
following Table 4-11 outlines the required UUID, revision, Arg1, Arg2 parameters, and
Error! Reference source not found. describes function definitions.
OSPM should use this _DSM when available. If this _DSM is not available, OSPM should use
Native PCIe Enclosure Management (NPEM) or SCSI Enclosure Services (SES) instead, if available.
Table 4-11:  _DSM Method Input Parameters
Argument Parameter
Arg0 UUID (set to 5D524D9D-FFF9-4D4B-8CB7-747ED51E194D).
Arg1 Revision ID (set to 1).
Arg2 Function Index as described in Error! Reference source not found..
Arg3
A package containing parameters for the function specified by the UUID, Revision
ID, and Function Index. The layout of the package for each Function Index along
with the corresponding output is illustrated in the following tables. The input and
output packages are a list of bytes (Buffer).

Table 4-12: Function Index
Index _DSM Function Name
0 Query supported functions (as per 9.1.1 of the ACPI 6.3 Specification).
1 Get PCIe SSD Supported LED States.
2 Get PCIe SSD Status LED State.
3 Set PCIe SSD Status LED State.
4 - 0xFFFF Reserved
