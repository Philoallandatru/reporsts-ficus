---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 65
headings: ["4.6.2. _DSM for PCI Express Slot Number"]
---

# Source page 65

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  65
 Integer 2:
Value  Meaning
 0h  Unknown
 1h  PCI Express Card Slot
 2h  PCI Express Server I/O Module Slot
 3h  PCI Express ExpressCard* Slto
 4h  PCI Express Mini Card Slot
 5h  PCI Express Wireless Form Factor Slot
 Others  Reserved
 This field indicates the type of the slot.
 Integer 3:
Bit      Position
0 SMBus signal
1 WAKE# signal
Others  Reserved
This field indicates the supported signal(s) of the slot.  More than one bit can be set in this
field to indicate the signals supported by the slot.
4.6.2. _DSM for PCI Express Slot Number
This section describes how PCI Express slot number information is exposed through the _DSM
ACPI method.  It provides a method to break the monolithic slot numbers that are already provided
both in ACPI firmware (through the _SUN method) and in PCI Express hardware (through the
PCI-to-PCI bridge Chassis ID and the PCI Express Slot Number) into tokens that each represent a
discrete hardware element.  This allows the slot numbers to be displayed to the user in a more
meaningful way.
This method only indicates the system-specific mechanism for interpreting the sub-fields of slot
numbers.  It does not mandate the exact format in which this data must be displayed to the user.
This method may exist in any device in the \_SB scope in the ACPI namespace.  The information
returned from this method applies to any PCI device underneath the device containing the method,
unless it is over-ridden by another instance of this method further down in the namespace tree.
The UUID in _DSM in this context is {E5C937D0-3553-4D7A-9117-EA4D19C3434D}, the
revision is 1, and the function is 2.
Note:  Function 0 is a generic Query function that is supported by _DSMs with any UUID and
Revision ID.  The definition of function 0 is generic to _DSM.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 1
Arg2: Function Index: 2
