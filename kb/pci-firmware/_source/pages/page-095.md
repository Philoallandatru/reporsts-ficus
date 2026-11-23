---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 95
headings: ["4.8. Generic ACPI PCI Slot Description"]
---

# Source page 95

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  95
Table 4-19: Function-specific Error Code for Function Index 3
Field Byte Length Byte Offset Description
Function-specific
Error Code
1 0 Bit [0] – Not all bits are set. If this bit is set, the
platform disregarded some or all of the
request state changes. OSPM should
check the resulting PCIe SSD Status LED
States to see what, if anything, has
changed.
Bit [1-7] – Reserved

4.8. Generic ACPI PCI Slot Description
To describe a PCI slot, either for manageability purposes or for supporting the ACPI-based PCI hot
plug, the ACPI namespace must list eight device objects corresponding to the possible eight
functions on the device in the slot.  For each of the device object, _ADR is used to identify the PCI
address (device number and function number) for each of the functions.  Note that each slot can
only support one device.
The following is an example name space for a slot:
            // Device definitions for Slot 1
            Device (S1F0) {    // Slot 1, Func#0
                Name(_ADR,0x00020000)
                Name(_SUN,0x00000001)
            }
            Device (S1F1) {    // Slot 1, Func#1
                Name(_ADR,0x00020001)
                Name(_SUN,0x00000001)
            }
            Device (S1F2) {    // Slot 1, Func#2
                Name(_ADR,0x00020002)
                Name(_SUN,0x00000001)
            }
            Device (S1F3) {    // Slot 1, Func#3
                Name(_ADR,0x00020003)
                Name(_SUN,0x00000001)
            }
            Device (S1F4) {    // Slot 1, Func#4
                Name(_ADR,0x00020004)
                Name(_SUN,0x00000001)
            }
            Device (S1F5) {    // Slot 1, Func#5
                Name(_ADR,0x00020005)
                Name(_SUN,0x00000001)
            }
            Device (S1F6) {    // Slot 1, Func#6
                Name(_ADR,0x00020006)
                Name(_SUN,0x00000001)
            }
            Device (S1F7) {    // Slot 1, Func#7
                Name(_ADR,0x00020007)
                Name(_SUN,0x00000001)
            }
