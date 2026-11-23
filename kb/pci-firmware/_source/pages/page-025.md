---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 25
headings: ["2.7.4. Read Configuration Word"]
---

# Source page 25

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  25
Input Register Requirements:
❑ If register DI has a register number less than or equal to 255 and does not have bit15=1, the
BIOS will read the configuration space and return the value read with return code “SUCCESS”.
❑ If register DI has a register number greater than 255 and does not have bit15=1, the BIOS will
not try to read the configuration space and returns “BAD_REGISTER_NUMBER”.
❑ If register DI has a register number greater than 255 with bit15=1 and the BIOS implements the
extensions for accessing PCI Express Extended Configuration space, then the BIOS will read
the configuration space and return the value read with return code “SUCCESS”.
❑ If register DI has a register number greater than 255 with bit15=1 and the BIOS does not
implement the extensions for accessing PCI Express Extended Configuration space, then the
BIOS will return error code of “FUNC_NOT_SUPPORTED”.
2.7.4. Read Configuration Word
This function allows reading individual words from the configuration space of a specific device.  The
Register Number parameter must be a multiple of two (i.e., bit 0 must be set to 0).
ENTRY:
 [AH] PCI_FUNCTION_ID
 [AL] READ_CONFIG_WORD
 [BH] Bus Number (0...255)
 [BL] Device Number in upper 5 bits,
  Function Number in lower 3 bits.
 [DI] Register Number (0, 2, 4,...4094) [bits 11:0]
   To Read Register number greater than 255 [bit15=1]
   To Read Register number less than or equal to 254 [bit15=0]
EXIT:
 [CX] Word Read
 [AH] Return Code:
   SUCCESSFUL
   BAD_REGISTER_NUMBER
   FUNC_NOT_SUPPORTED
 [CF] Completion Status, set = error, reset = success.
