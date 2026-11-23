---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 63
headings: ["4.6.1. _DSM for PCI Express Slot Information"]
---

# Source page 63

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  63
OSPM must invoke all Functions other than Function 0 with the same Revision ID value. The
Revision ID value is determined by OSPM’s invocation of Function 0 with the highest known
(Current Revision ID) value for the Revision ID. If system firmware returns an empty Buffer or a
Buffer containing a single entry with a value of 0 (no bits set), the UUID is unknown and OSPM
should not attempt to invoke any Functions with that UUID. If system firmware returns a Buffer
containing a single entry with a value of 1 (bit 0 set), the UUID is known and supported by system
firmware, but the Revision ID is unknown. If this occurs, OSPM should successively invoke
Function 0 with decremented values of Revision ID until system firmware returns a value indicating
support for more than Function 0.
Table 4-7:  _DSM Definitions for PCI
UUID Initial Revision ID Function Description
E5C937D0-3553-4D7A-9117-
EA4D19C3434D
1 1 PCI Express Slot Information
1 2 PCI Express Slot Number
1 3 Vendor-specific Token ID
1 4 PCI Bus Capabilities
2 5 Preserve PCI Boot Configuration
2 6 LTR Maximum Latency
2 7 Naming a PCI or PCI Express device
under OS
3 8 Avoid power-on Reset Delay
Duplication on Sx Resume
3 9 Device Readiness Durations
4 0Ah Request D3cold Aux Power Limit
4 0Bh Add PERST# Assertion Delay
5 0Ch Downstream Port Containment and Hot-
Plug Surprise Control
5 0Dh Locate the port that experienced the
containment event
6 0Eh Query Platform Vendor Specific TPH
Features
4.6.1. _DSM for PCI Express Slot Information
This section describes how the PCI Express slot information is exposed through the _DSM ACPI
method.  In the future, this information may be reported through hardware mechanisms that the
operating system has direct access to; if and when that is available, the information provided through
the hardware mechanism overrides the information provided through the mechanism defined in this
section.  The operating system should not use the mechanism defined in this section.
Note:  The SMBIOS Specification defines the Type 9 entry structure and enumerations that allows
reporting slot information for PCI/PCI-X/PCI Express slots.  However, the SMBIOS access
mechanism does not comprehend platforms with dynamic characteristics that would render statically
reported SMBIOS data invalid.  _DSM mechanism is used on such platforms to report the
equivalent of the SMBIOS Type 9 slot information.  The UUID in _DSM in this context is
{E5C937D0-3553-4D7A-9117-EA4D19C3434D}, the revision is 1, and the function is 1.
