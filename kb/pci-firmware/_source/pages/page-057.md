---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 57
headings: []
---

# Source page 57

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  57
Control Field
Bit Offset Interpretation
If control of this feature was requested and denied, or was not requested, then
the operating system is permitted to write to the following:

• DPC Status bit in the DPC Status Register
• Device Status Register
• Uncorrectable Error Status Register
• Correctable Error Status Register

in any PCI Function below the port that triggered DPC after firmware returns
from the _OST corresponding to the Error Disconnect Recover notification but
before the operating system finishes re-initializing the Function or disables the
Function. During that time, firmware is prohibited from writing to the DPC Status
Register, Device Status Register, Uncorrectable Error Status Register, and
Correctable Error Status Register in any PCI Function below the port that
triggered DPC.

8 PCI Express Completion Timeout Control
The firmware sets this bit to 1 to grant control over the PCI Express Completion
Timeout fields. If the firmware does not grant control of this feature, firmware
must handle configuration of the PCI Express Completion Timeout fields.
If firmware grants the operating system control of this feature, any firmware
configuration of the PCI Express Completion Timeout fields may be overwritten
by an operating system configuration, depending on operating system policy.
These fields include Completion Timeout Value (Device Control 2 Register bits
3:0 in the PCI Express Capability Structure) and Completion Timeout Disable
(Device Control 2 Register bit 4 in the PCI Express Capability Structure). If the
operating system successfully receives control of this feature, it is responsible
for configuring the PCI Express Completion Timeout fields in a manner that
complies with the PCI Express Base Specification.
Additionally, the operating system is responsible for saving and restoring all PCI
Express Completion Timeout field settings across power transitions to and from
S1, S2, S3 system power states when register context may have been lost.
If control of this feature was requested and denied, or was not requested, the
firmware returns this bit set to 0, and the operating system must not modify PCI
Express Completion Timeout fields.
If the firmware does not grant control of this feature, firmware must handle
configuration of the PCI Express Completion Timeout fields.
