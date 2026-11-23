---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 16
headings: ["2.5.3. Find PCI Device"]
---

# Source page 16

TRADITIONAL PCI BIOS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  16
2.5.3. Find PCI Device
This function returns the location of PCI devices that have a specific Device ID and Vendor ID.
Given a Vendor ID, Device ID, and an Index (N), the function returns the Bus Number, Device
Number, and Function Number of the Nth Device/Function whose Vendor ID and Device ID
match the input parameters.
ENTRY:
 [AH]   PCI_FUNCTION_ID
 [AL]  FIND_PCI_DEVICE
 [CX]  Device ID (0...65535)
 [DX]  Vendor ID (0...65534)
 [SI]  Index (0...N)
EXIT:
 [BH]  Bus  Number (0...255)
 [BL]  Device Number in upper 5 bits,
   Function Number in bottom 3 bits.
 [AH]  Return Code:
    SUCCESSFUL
    DEVICE_NOT_FOUND
    BAD_VENDOR_ID
 [CF]  Completion Status, set = error, cleared = success.
Calling software can find all devices having the same Vendor ID and Device ID by making
successive calls to this function starting with Index set to zero, and incrementing it until the return
code is “DEVICE_NOT_FOUND”.  A return code of BAD_VENDOR_ID indicates that the
passed in Vendor ID value (in [DX]) had an illegal value of all 1's.
Values returned by this function upon successful completion must be the actual values used to
access the PCI device if the INT 1Ah routines are bypassed in favor of the direct I/O mechanisms
described in the PCI Specification.
