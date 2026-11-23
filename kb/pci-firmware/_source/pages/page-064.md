---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 64
headings: []
---

# Source page 64

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  64
Note:  Function 0 is a generic Query function that is supported by _DSMs with any UUID and
Revision ID.  The definition of function 0 is generic to _DSM.
Location:
This object will be placed under the virtual PCI-to-PCI bridge object representing the PCI Express
root port or switch port that generates the slot on the motherboard.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 1
Arg2: Function Index: 1
Return:
ACPI Buffer type; the definition of the return is a package of two items and the description is as
follows:
Package item 1:
Type: Integer
Purpose: status of operation
Description:
0: Failure
1: Success
Package item 2:
Type: Package
Purpose: PCI Express Slot Information
Description: A package of three integers:
 Integer 1:
Bit      Position
0 Supports x1
1 Supports x2
2 Supports x4
3 Supports x8
4 Supports x12
5 Supports x16
Others Reserved
This integer indicates the link width capabilities of the slot.  More than one bit can be set in
this field to indicate the link widths supported by the slot.  For example, a x8 slot that is
capable of supporting x4, x2, and x1 would be indicated by setting bits 0, 1, and 2 in this
field.  This field indicates the downshift capabilities to management software.  For maximum
and negotiated link width, refer to the PCI Express Base Specification.
