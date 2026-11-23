---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 66
headings: []
---

# Source page 66

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  66
Return:
A Package of token packages.  The returned package must contain at lease one token package.
Each sub-package represents a slot number token, which is a bit range within one of the monolithic
slot numbers that has a distinct meaning.  For example, bits 4-7 of the PCI Express Slot Number
could represent the I/O Cabinet the slot sits in, while bits 0-3 would be the slot number within the
cabinet.  Each of these fields would be represented by a different token.
Each token is a package of four items:
Source ID – This field indicates the source data of the bit range that this token represents.
Token ID – This field indicates the type of element the token represents.  Token IDs 0-7Fh
are reserved by this specification.  Token IDs 80h - FFhare vendor-specific.
Start bit – This field indicates the first bit number of the token in the source data.
End bit – This field indicates the last bit number of the token in the source data.
Token IDs:
0 – Chassis
1 – Cabinet
2 – I/O Tray
3 – Module
4 – Slot
5-7Fh – Reserved
80h-FFh – Vendor-specific
Source IDs:
0 – The _SUN method in the ACPI namespace
1 – The data in the Chassis ID register of the PCI-to-PCI bridge Slot Numbering Capability
2 – The data in the Physical Slot Number field of the Slot Capabilities register in the PCI
       Express Capability
Example:
    Method (_DSM, 3) {    // Assume GUID and revision match
     Return (Package(3){    // PCI Express Slot Parsing
   Package(4){
    1,1,2,7       // bit 7:2 in the PPB Chassis ID
   },        // Token represents a “Cabinet”
   Package(4){
    1,2,0,1     // bit 1:0 in the PPB Chassis ID
   },        // Token represents an “I/O Tray”
   Package(4){
    2,4,0,7     // bit 7:0 in the PCI Express Physical
   }        // Slot Number
  })
   }

If the PPB Chassis ID of a device in the hierarchy under the location of this method contained the
value 0100 1110b and the PCI Express Physical Slot Number contained 17Ah, the device’s slot
number could be displayed as “Cabinet 13h, I/O Tray 2, Slot 7Ah”.
