---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 30
headings: ["2.8. Function List"]
---

# Source page 30

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  30
Input Register Requirements:
❑ If register DI has a register number less than or equal to 252 and does not have bit15=1, the
BIOS will read the configuration space and return the value read with return code “SUCCESS”.
❑ If register DI has a register number greater than 255 and does not have bit15=1, the BIOS will
not try to read the configuration space and returns “BAD_REGISTER_NUMBER”.
❑ If register DI has a register number greater than 255 with bit15=1 and the BIOS implements the
extensions for accessing PCI Express Extended Configuration space, then the BIOS will read
the configuration space and return the value read with return code “SUCCESS”.
❑ If register DI has a register number greater than 255 with bit15=1 and the BIOS does not
implement the extensions for accessing PCI Express Extended Configuration space, then the
BIOS will return error code of “FUNC_NOT_SUPPORTED”.
2.8. Function List
Table 2-3:  Function List
Function AH AL Implementation Notes
PCI_FUNCTION_ID B1h
PCI_BIOS_PRESENT  01h
FIND_PCI_DEVICE  02h Optional  1
FIND_PCI_CLASS_CODE  03h Optional  1
GENERATE_SPECIAL_CYCLE  06h Optional  1
READ_CONFIG_BYTE  08h Optional  1
READ_CONFIG_WORD  09h Optional  1
READ_CONFIG_DWORD  0Ah Optional  1
WRITE_CONFIG_BYTE  0Bh Optional  1
WRITE_CONFIG_WORD  0Ch Optional  1
WRITE_CONFIG_DWORD  0Dh Optional  1
GET_IRQ_ROUTING_EXPANSIONS  0Eh Optional  2
SET_PCI_HW_INT  0Fh Optional  2
Notes:
1. If the “PCI BIOS PRESENT (B101h)” function indicates “Presence”, then all functions (06h-to-0Dh
inclusively) must be implemented for register accesses below 256 and must be present during
POST and at run-time (after POST completes).  For register accesses above 255, these functions
must only be present during POST.  There is not a requirement to implement the above 255
register access functions after POST completes; however, if implemented, they must not change
the processor mode when invoked after POST (option ROMs might be executing in v86 mode).
2. Implementation of these INT1Ah sub-functions is optional for compliance with this version of the
specification.
