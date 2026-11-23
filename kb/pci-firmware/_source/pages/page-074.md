---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 74
headings: []
---

# Source page 74

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  74
● Instance number must be unique under \_SB scope.  This instance number does not have to
be sequential in a given system configuration.
● This entry is mandatory when this _DSM is implemented.
● In typical usage model, in a configuration with multiple devices of the same type, device with
lower instance number would be assigned lower device label by the operating system
compared to another device with higher instance number.
❑ Second  entry of the package is a string name:
● This string is optional even when this _DSM is implemented; when not implemented, this
entry must return a null string.
● When populated, this string object should match the label/name on the chassis.  String
should be specified in Unicode.
● When implemented, this string must be unique for a given platform under \_SB.
This interface is defined for devices that are defined in ACPI namespace for a given platform by the
BIOS.  For expansion slots, typically, platform BIOS will include entry for the PCI or PCI Express
slot in its namespace and each of these expansion slots would be expected to include their respective
_DSM entries.  Assignment of specific device names to multi-function devices installed in expansion
slots, and/or PCI or PCI Express devices that are hot-added to expansion slots in operating system-
environment would be handled in operating system-specific manner, and is not specified via this
specification.
Location:
This object will be placed under the ACPI object representing the embedded PCI or PCI Express
device/function or under the ACPI PCI Slot description (as defined in Section 4.7) representing the
add-in PCI or PCI Express Slot.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 2
Arg2: Function Index: 7
Arg3: None
Return:
A package of two elements.

Method (_DSM, 3) { // Assume GUID and revision match

  If (LAnd( Lequal(Arg1, 2), Lequal(Arg2,7))) {
    Return ( Package(2){ // PCI Express Slot Parsing
  1,  // Instance of the enumeration
  String1 //String name which matches the label on the chassis
    }
  } // end of If (LAnd...
} // end of method
