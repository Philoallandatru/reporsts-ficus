---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 60
headings: ["4.5.2.4. Dependencies Between _OSC Control Bits"]
---

# Source page 60

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  60
4.5.2.4. Dependencies Between _OSC Control Bits
Because handling of hot-plug events, power management events, advanced error reporting,
downstream port containment, and completion timeout all require the modification of PCI Express
Capability registers, the operating system is required to claim control over the PCI Express
Capability (bit 4 of the Control field) in conjunction with claiming control over PCI Express Native
Hot Plug, PCI Express Native Power Management Events, PCI Express Advanced Error Reporting,
Latency Tolerance Reporting, Downstream Port Containment, or PCI Express Completion Timeout
(bits 0, 2, 3, 5, 7 and 8 of the Control field).  If the operating system attempts to claim control of any
of these features without also claiming control over the PCI Express Capability, the firmware is
required to refuse control of the feature being illegally claimed and mask the corresponding bit.
Because handling of Downstream Port Containment has a dependency on Advanced Error
Reporting, the operating system is required to request control over Advanced Error Reporting (bit 3
of the Control field) while requesting control over Downstream Port Containment Configuration
(bit 7 of the Control field). If the operating system attempts to claim control of Downstream Port
Containment Configuration without also claiming control over Advanced Error Reporting, firmware
is required to refuse control of the feature being illegally claimed and mask the corresponding bit.
Firmware is required to maintain ownership of Advanced Error Reporting if it retains ownership of
Downstream Port Containment Configuration.
If the operating system sets bit 7 of the Control field, it must set bit 7 of the Support field, indicating
support for the Error Disconnect Recover event.
Operating systems must comprehend that platforms may not grant control of the PCI Express
Advanced Error Reporting feature and PCI Express Downstream Port Containment Configuration
feature.
If firmware does not support _DSM for Downstream Port Containment Enable and Hot-Plug
Surprise Control, then Operating Systems, drivers, and software determine that slots in the platform
support surprise removal by consulting the Hot-Plug Surprise bit in the Slot Capabilities register of
corresponding root port or switch downstream port.
If firmware does support _DSM for Downstream Port Containment Enable and Hot-Plug Surprise
Control, then the Hot-Plug Surprise bit may be cleared by the platform and therefore, it is
recommended that firmware advertise whether or not slots in the platform support surprise removal
(also referred to as ‘async removal’) via bit 4 of Slot Characteristics 2 in the SMBIOS Type 9
structure (System Slots). Refer to the SMBIOS Reference Specification, Version 3.4.0a or newer for
details on bit 4 of Slot Characteristics 2 in the SMBIOS Type 9 structure.
