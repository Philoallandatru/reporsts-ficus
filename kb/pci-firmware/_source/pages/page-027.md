---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 27
headings: ["2.7.6. Write Configuration Byte"]
---

# Source page 27

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  27
Input Register Requirements:
❑ If register DI has a register number less than or equal to 252 and does not have bit15=1, the
BIOS will read the configuration space and return the value read with return code “SUCCESS”.
❑ If register DI has a register number greater than 255 and does not have bit15=1, the BIOS will
not try to read the configuration space and returns “BAD_REGISTER_NUMBER”.
❑ If register DI has a register number greater than 255 with bit15=1 and BIOS implements the
extensions for accessing PCI Express Extended Configuration space, then the BIOS will read
the configuration space and return the value read with return code “SUCCESS”.
❑ If register DI has a register number greater than 255 with bit15=1 and the BIOS does not
implement the extensions for accessing PCI Express Extended Configuration space, then the
BIOS will return error code of “FUNC_NOT_SUPPORTED”.
2.7.6. Write Configuration Byte
This function allows writing individual bytes to the configuration space of a specific device.
ENTRY:
 [AH]  PCI_FUNCTION_ID
 [AL]  WRITE_CONFIG_BYTE
 [BH]  Bus Number (0...255)
 [BL]  Device Number in upper 5 bits,
   Function Number in lower 3 bits.
 [DI]  Register Number (0...4095) [bits 11:0]
   To Write Register number greater than 255 [bit15=1]
   To Write Register number less than or equal to 255 [bit15=0]
 [CL]  Byte Value to Write
EXIT:
 [AH]  Return Code:
    SUCCESSFUL
    BAD_REGISTER_NUMBER
    FUNC_NOT_SUPPORTED
 [CF]  Completion Status, set = error, reset = success.
