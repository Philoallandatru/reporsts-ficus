---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 51
headings: []
---

# Source page 51

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  51
Support Field
Bit Offset
Interpretation
8 _HPX PCI Express Descriptor Setting Record (Type 3) Supported
The operating system sets this bit to 1 if it supports _HPX PCI Express Descriptor
Setting Record (Type 3). Otherwise, the operating system sets this bit to 0.
9:31 Reserved



IMPLEMENTATION NOTE
Recommended Use of ASPM Optionality Support Bit
The ASPM Optionality bit in the _OSC Support field is designed to be used by platform firmware for
use with devices known a priori by platform firmware to have an ASPM Support field that is write -
once or otherwise lockable, configurable by platform firmware, and support ASPM L1 but do not
support L0s.
In the case where the operating system does not support ASPM Optionality, such devices would be
configured by firmware to report support for both L0s and ASPM L1.
In the case where the operating system supports ASPM Optionality, such devices would be
configured to report support for only ASPM L1.



Table 4-5:  Interpretation of the _OSC Control Field, Passed in via Arg3
Control Field
Bit Offset Interpretation
0 PCI Express Native Hot Plug control
The operating system sets this bit to 1 to request control over PCI Express native
hot plug.
If the operating system sets this bit, it must also set bit 4 to request control of the
PCI Express Capability Structure.
1 SHPC Native Hot Plug control
The operating system sets this bit to 1 to request control over PCI/PCI-X SHPC
hot plug.
If the operating system sets this bit, it must also set bit 4, PCI Express Capability
Structure control, to request control of the PCI Express Capability Structure.
2 PCI Express Native Power Management Events control
The operating system sets this bit to 1 to request control over PCI Express native
power management event interrupts (PMEs).
If the operating system sets this bit, it must also set bit 4, PCI Express Capability
Structure control, to request control of the PCI Express Capability Structure.
3 PCI Express Advanced Error Reporting control
The operating system sets this bit to 1 to request control over the PCI Express
Advanced Error Reporting Extended Capability structure, if supported, and the
other error enable/status bits defined in the PCI Express Base Specification.
If the operating system sets this bit, it must also set bit 4, PCI Express Capability
Structure control, to request control of the PCI Express Capability Structure.
