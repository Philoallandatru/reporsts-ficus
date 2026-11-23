---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 104
headings: []
---

# Source page 104

PCI EXPANSION ROMS
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  104
6. If Vendor ID matches but the Device ID does not, the POST Firmware will examine the Device
List Pointer.  Assuming the Device List Pointer is not zero, the POST firmware will examine the
Device List to find a match to the Device ID in the device.  A value of 0000h indicates the end
of the Device List.
Note that Expansion ROMs of Code Type 3 (UEFI) do not support the Device List Pointer.
For other Code Types, only Expansion ROMs compliant to this specification version 3.0 or later
support the Device List Pointer.  POST Firmware should not examine the Device List Pointer
field until it has confirmed that the PCI Data Structure Revision Level is 3 or greater.
7. After finding the proper image, the POST Firmware determines if there is sufficient space for
the image to be copied into RAM in preparation for initialization.  This is accomplished by
examining the Maximum Run-Time Image Length field.
Note that only Expansion ROMs compliant to this specification version 3.0 or later support the
Maximum Run-Time Image Length field.  POST Firmware should not examine the Maximum
Run-Time Image Length field until it has confirmed that the PCI Data Structure Revision Level
is 3.
Note that if the image is a PCI 2.1 compliant Expansion ROM, the POST firmware must
continue examining the images to determine if an Expansion ROM compliant to this
specification version 3.0 or later exists for the same Vendor ID and Device ID.  Expansion
ROMs compliant to this specification version 2.1 or earlier must only be used by the POST
firmware when an Expansion ROM compliant to this specification version 3.0 or later cannot be
found.
8. The System firmware must confirm that the Option ROM image has a valid checksum before
copying it into RAM.  This checksum is calculated using Current Image Size as described in
Section 5.2.1.4.
9. The POST firmware then copies the appropriate amount of data into RAM.  The amount of
data to copy is determined by examining the Image Length field in the PCI Data structure in the
header.
10. The POST firmware then disables the Expansion ROM Base Address register.
Subsequent steps will vary depending on the value of the Code Type field.
