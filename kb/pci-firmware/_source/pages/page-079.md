---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 79
headings: ["4.6.10. _DSM for Requesting D3cold Aux Power Limit"]
---

# Source page 79

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  79
4.6.10. _DSM for Requesting D3cold Aux Power Limit
The Request D3cold Aux Power Limit function describes how a device driver conveys its auxiliary
power requirements to the host platform when the device is in D3cold. The system firmware
responds with a value indicating whether the request can be supported. The power request is specific
to the Auxiliary power supply; main power8 may be removed while in D3cold. A device must not
draw any more power than what has been negotiated via this mechanism after entering D3cold.
A device driver may invoke this function multiple times, either to determine the maximum available
power, to retry a request that was temporarily rejected, or to modify (raise or lower) the amount of
required power.
For a Multi-Function Device, the driver for Function 0 is required to report an aggregate power
requirement covering all functions contained within the device.
Earlier power limits are superseded when this function grants a request. In all other cases, this
function has no effect on earlier power limits. This includes grants from earlier calls of this function
as well as requirements for the D3 PM state in the form factor and PCI Express Base Specification.
Location:
Support for the Request D3cold Aux Power Limit function is only applicable for a _DSM Control
Method within the scope of a PCI Express Downstream Port.
For bus hierarchies where multiple Functions reside beneath the PCI Express Downstream Port
supporting this _DSM function, system software is responsible for tracking and aggregating requests
from child devices and requesting the sum of the requested power limits.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 4
Arg2: Function Index: 0Ah
Arg3: Integer. The value of the integer is the amount of power requested, in mW, for the
auxiliary power supply. The minimum allowed value is 0; the maximum allowed value
varies by form factor. A value of 8000 0000h signifies that the hierarchy connected via
the slot cannot support main power removal when in D3cold while the system is in S0.

8 This term “main power” matches the usage in the PCI Express Card Electromechanical Specification, for other form
factors, a mapping to proper terminology may be needed.
