---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 55
headings: []
---

# Source page 55

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  55
Control Field
Bit Offset Interpretation
4 PCI Express Capability Structure control
The firmware sets this bit to 1 to grant control over the PCI Express Capability,
the Virtual Channel Extended Capability, the Power Budgeting Extended
Capability, the Advanced Error Reporting Extended Capability, and the Serial
Number Extended Capability.
If the firmware does not grant control of this feature, firmware must handle
configuration of these Capabilities.
If firmware grants the operating system control of this feature, any firmwar e
configuration of these Capabilities may be overwritten by an operating system
configuration, depending on operating system policy.
If the operating system successfully receives control of this feature, it is
responsible for configuring the registers in these Capabilities in a manner that
complies with the PCI Express Base Specification.
Additionally, the operating system is responsible for saving and restoring all
settings within these Capabilities registers listed above across power transitions
to and from S1, S2, S3 system power states when register context may have
been lost.
If control of this feature was requested and denied or was not requested,
firmware returns this bit set to 0, and the operating system must not modify
these Capabilities.
5 Latency Tolerance Reporting control
The firmware sets this bit to 1 to grant control over control over PCI Express
Latency Tolerance Reporting.
If firmware allows the operating system control of this feature, then in the context
of the _OSC method, the firmware must ensure that the LTR Extended
Capabilities Structure is initialized properly in all devices that support LTR as
described in the PCI Express Base Specification.  If control of this feature was
requested and denied or was not requested, firmware returns this bit set to 0.
If the operating system successfully receives control of this feature, it must
manage configuration of the LTR Extended Capability structure and LTR
Mechanism Enable fields as described in the PCI Express Base Specification.
Additionally, the operating system is responsible for saving and restoring LTR
configuration across power transitions to and from S1, S2, S3 system power
states when register context may have been lost.
If control of this feature was requested and denied or was not requested,
firmware returns this bit set to 0, and the operating system must not modify LTR
Capabilities.
6 The firmware sets this bit to 1 to indicate that it will suppress error notification
caused by surprise hot remove (Completion Time Out errors).
