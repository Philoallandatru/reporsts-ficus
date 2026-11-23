---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 54
headings: []
---

# Source page 54

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  54
Control Field
Bit Offset Interpretation
2 PCI Express Native Power Management Events control
The firmware sets this bit to 1 to grant control over control over PCI Express
native power management event interrupts (PMEs).
If firmware allows the operating system control of this feature, then in the context
of the _OSC method, it must ensure that all PMEs are routed to Root Port
interrupts as described in the PCI Express Base Specification.  Additionally, after
control is transferred to the operating system, firmware must not update the PME
Status field in the Root Status register or the PME Interrupt Enable field in the
Root Control register.
If the operating system successfully receives control of this feature, it must
handle power management events as described in the PCI Express Base
Specification.
If control of this feature was requested and denied or was not requested,
firmware returns this bit set to 0.
3 PCI Express Advanced Error Reporting control
The firmware sets this bit to 1 to grant control over the PCI Express Advanced
Error Reporting Capability structure, if supported, and the other error
enable/status bits defined in the PCI Express Base Specification:
• Correctable Error Reporting Enable
• Non-Fatal Error Reporting Enable
• Fatal Error Reporting Enable
• Unsupported Request Reporting Enable
• Correctable Error Detected
• Non-Fatal Error Detected
• Fatal Error Detected
• Unsupported Request Detected
If firmware allows the operating system control of this feature, then in the context
of the _OSC method, it must ensure that error messages are routed to device
interrupts as described in the PCI Express Base Specification.  Additionally, after
control is transferred to the operating system, firmware must not modify the
Advanced Error Reporting Capability and the other error enable/status bits listed
above.
If firmware grants control of Advanced Error Reporting, it must also grant control
of the PCI Express Capability structure (bit 4).  If firmware retains ownership of
Downstream Port containment, it must also retain ownership of Advanced Error
Reporting.
Additionally, the operating system retains control of AER and the other error
enable/status bits across power transitions to and from S1, S2, S3 system power
states, and is responsible for saving and restoring the AER and error enable
configuration across those transitions when register context may have been lost.
If control of this feature was requested and denied or was not requested,
firmware returns this bit set to 0, and the operating system must not modify the
Advanced Error Reporting Capability or the other error enable/status bits listed
above.
