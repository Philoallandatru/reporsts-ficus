---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 58
headings: []
---

# Source page 58

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  58
Control Field
Bit Offset Interpretation
9 PCI Express System Firmware Intermediary Configuration Control
Firmware sets this bit to 1 to grant the operating system control over PCI
Express System Firmware Intermediary configuration.
If firmware grants the operating system control of this feature, then the operating
system is responsible for initializing System Firmware Intermediary Extended
Capability Structure; further, the operating system retains control of SFI across
power transitions for S1, S2, S3 system power states.
If this bit is set by the operating system, this indicates that it supports both native
operating system control and firmware ownership models of SFI.
If control of this feature was requested and denied, or was not requested, the
firmware returns this bit set to 0, and the operating system must not modify
System Firmware Intermediary registers.
If control of this feature was requested and denied, firmware is responsible for
initializing System Firmware Intermediary Extended Capability Structures per
firmware policy.
10 – 31 Reserved
