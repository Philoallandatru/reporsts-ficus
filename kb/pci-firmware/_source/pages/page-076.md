---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 76
headings: ["4.6.8. _DSM for Avoiding Power-On Reset Delay Duplication on Sx Resume"]
---

# Source page 76

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  76
4.6.8. _DSM for Avoiding Power-On Reset Delay
Duplication on Sx Resume
This section describes how system firmware can inform operating system that no additional delay is
needed before issuing the first Configuration Access to a device in the PCI subsystem underneath
the host bus. System hardware/firmware assume the responsibility of providing the post power-on
delay (Conventional Reset delay and Data Link Up (DL_Up) Time delay).
This function is optional. If not present, the operating system should adhere to the post
Conventional Reset delays as described in the PCIe Base Specification.
If system firmware assumes the responsibility of post Conventional Reset delay (and informs the
Operating System via this _DSM function) on Sx Resume (such as boot from ACPI S5, or resume
from ACPI S4 or S3 states), the Operating System may assume sufficient time has elapsed since the
end of reset, and devices within the PCI subsystem are ready for Configuration Access.
It is the system integrator’s responsibility to ensure that the pre-OS power-on delay sequence covers
all devices in the PCI subsystem. If the system firmware supports runtime power gating on any of
the device within PCI subsystem covered by this _DSM function, the system firmware is responsible
for covering the necessary post power-on reset delay.
If an Operating System (after it has control of the PCI subsystem) has the ability to apply
Conventional Reset to devices without system firmware involvement, then it will need to adhere to
delays after such reset.
This _DSM function is applicable whether reduction in device readiness timing, via Readiness
Notification or _DSM function 9, are available or not.
The returned value of this _DSM function also applies to PCI devices integrated into the Root
Complex within the PCI hierarchy.
Location:
This object can only be placed within the scope of a PCI host bus. This _DSM function is intended
to cover the PCI subsystem underneath the host bus. If a _DSM Method implementing this
function is found within the scope of any other device, any values returned by this function should
be ignored.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 3
Arg2: Function Index: 8
Arg3: Empty Package
