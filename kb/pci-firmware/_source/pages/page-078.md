---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 78
headings: []
---

# Source page 78

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  78
 IMPLEMENTATION NOTE
It is recommended that the ASL constant of Ones be used for any element in the returned package
where overriding the default value is not desired.
For systems where FRS and DRS messages are supported and enabled, it is expected that FRS
and DRS Events will only be overridden by this _DSM function in cases where these Events are
determined to be problematic or sub-optimal by the system vendor.

Location:
This object can be placed within the scope of any PCI device object, including RCIE scope, PCI
devices integrated into the Root Complex, and all other PCI Express functions. The delay values
returned by this function are only applicable to the device object. Downstream devices (if any) will
retain the default delay requirement according to PCI Express Base Specification and/or applicable form
factor specification.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 3
Arg2: Function Index: 9
Arg3: Empty Package
Return:
A Package of five integers covering the various device related delay in the PCIe Base Specification:
Integer 0: FW Reset Time-- Number of microseconds that the operating system should wait after a
Conventional Reset, before issuing the first Configuration Access. For downstream ports
supporting the Data Link Layer Active Reporting capability, this entry should not be
used. This value may also be specified for PCI devices integrated into the Root Complex.
Integer 1: FW DL_Up Time-- Number of microseconds that the operating system should wait
after the Downstream Port above this device reports Data Link Layer Link Active,
before issuing the first Configuration Access. This entry should only be used for
downstream ports supporting the Data Link Layer Active Reporting Capability.
Integer 2: FW FLR Reset Time-- Number of microseconds that the operating system should wait
after an FLR, before issuing the first Configuration Access.
Integer 3: FW D3hot to D0 Time-- Number of microseconds that the operating system should
wait on D3hot-to-D0 transition, before issuing the first request (Configuration Access or
any other Request). This value may also be specified for PCI devices integrated into the
Root Complex.
Integer 4: FW VF Enable Time-- Number of microseconds that the operating system should wait
after setting the VF Enable bit, before issuing the first request (Configuration Access or
any other Request) to respective VFs.
