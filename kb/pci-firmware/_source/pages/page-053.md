---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 53
headings: []
---

# Source page 53

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  53
Table 4-6:  Interpretation of the _OSC Control Field, Returned Value
Control Field
Bit Offset Interpretation
0 PCI Express Native Hot Plug control
The firmware sets this bit to 1 to grant control over PCI Express native hot plug
interrupts.
If firmware allows the operating system control of this feature, it means that the
firmware has made the necessary configurations to ensure that all hot plug
events are routed to device interrupts as described in the PCI Express Base
Specification (e.g., switched from SCI/GPE interrupt mechanism used in the
legacy hot plug mechanisms), regardless of whether there are hot pluggable
slots down the hierarchy.
It is the operating system’s responsibility to determine whether a slot is hot
pluggable by examining the status of the slots based on the PCI Express Base
Specification.  Additionally, after control is transferred to the operating system,
firmware must not update the state of hot plug slots, including the state of the
indicators and power controller.
If control of this feature was requested and denied or was not requested,
firmware returns this bit set to 0.
1 SHPC Native Hot Plug control
The firmware sets this bit to 1 to grant control over PCI/PCI-X SHPC hot plug.
If firmware allows the operating system control of this feature, it means that the
firmware has made the necessary configurations to ensure that all hot plug
events are routed to device interrupts as described in the PCI SHPC
Specification 1.0 (e.g., switched from SCI/GPE interrupt mechanism used in the
legacy hot plug mechanisms), regardless of whether there are hot pluggable
slots down the hierarchy.
If the operating system successfully receives control of this feature, it must track
and update the status of hot plug slots and handle hot plug events as described
in the SHPC Specification.
It is the operating system’s responsibility to determine whether a slot is hot
pluggable by examining the status of the slots based on the PCI SHPC
Specification.  Additionally, after control is transferred to the operating system,
firmware must not update the state of hot plug slots, including the state of the
indicators and power controller.
If control of this feature was requested and denied or was not requested,
firmware returns this bit set to 0.
System firmware must always assume that PCI-X features are supported
beneath a PCI Express hierarchy unless it has explicit knowledge to the
contrary, and must not mask this bit to zero in PCI Express hierarchy.
