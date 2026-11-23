---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 17
headings: ["2.5.4. Find PCI Class Code"]
---

# Source page 17

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  17
2.5.4. Find PCI Class Code
This function returns the location of PCI devices that have a specific Class Code.  Given a Class
Code and an Index (N), the function returns the Bus Number, Device Number, and Function
Number of the Nth Device/Function whose Class Code matches the input parameters.
ENTRY:
 [AH]   PCI_FUNCTION_ID
 [AL]  FIND_PCI_CLASS_CODE
 [ECX]  Class Code (in lower 3 bytes)
 [SI]  Index (0...N)
EXIT:
 [BH]  Bus Number (0...255)
 [BL]  Device Number in upper 5 bits,
   Function Number in bottom 3 bits.
 [AH]  Return Code:
    SUCCESSFUL
    DEVICE_NOT_FOUND
 [CF]  Completion Status, set = error, cleared = success.
Calling software can find all devices having the same Class Code by making successive calls to this
function starting with Index set to zero, and incrementing it until the return code is
“DEVICE_NOT_FOUND”.
