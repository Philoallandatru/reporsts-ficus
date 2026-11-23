---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 56
headings: []
---

# Source page 56

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  56
7 PCI Express Downstream Port Containment configuration control
Firmware sets this bit to 1 to grant the operating system control over PCI
Express Downstream Port Containment configuration.

If firmware grants control of Downstream Port Containment, it must also grant
control of the Advanced Error Reporting and PCI Express Capability Structures.
If firmware retains ownership of Downstream Port containment, it must also
retain ownership of Advanced Error Reporting.

If firmware allows the operating system control of this feature, then, in the
context of the _OSC method firmware must clear the DPC ERR_COR Enable bit
in the DPC Control Register (refer to the PCI Express Base Specification) to 0.
Additionally, after control is transferred to the operating system, firmware must
not modify any registers in the Downstream Port Containment Extended
Capability Structure. Any firmware configuration of the Downstream Port
Containment Capability may be overwritten by the operating system, depending
on operating system policy.
If control of this feature was requested and denied, or was not requested, the
firmware sets this bit to 0, and the operating system must not modify
Downstream Port Containment Capabilities except as provided below.
If control of this feature was requested and denied, or was not requested,
firmware is responsible for initializing Downstream Port Containment Extended
Capability Structures per firmware policy. Further, the operating system is
permitted to write the following:

• Device Status Register
• Uncorrectable Error Status Register
• Correctable Error Status Register
• Root Error Status Register
• RP PIO Status Register

in the Port that triggered DPC while processing an Error Disconnect Recover
notification from firmware. The Error Disconnect Recover notification processing
window begins with the Error Disconnect Recover Notify from firmware and ends
when the operating system invokes the _OST method to inform firmware of the
status of the Error Disconnect Recover notification. During this window, firmware
is not permitted to write to these registers.

If control of this feature was requested and denied, or was not requested, then
the operating system is permitted to write to the DPC Trigger Status bit in the
DPC Status Register in the Port that triggered containment and firmware is
prohibited from writing to the DPC Status Register:

• during the Error Disconnect Recover notification processing window
• while processing the subsequent hot-remove of a device under a port with the
DPC Trigger Status bit set to 1.
