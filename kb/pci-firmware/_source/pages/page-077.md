---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 77
headings: ["4.6.9. _DSM for Specifying Device Readiness Durations"]
---

# Source page 77

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  77
Return:
An integer whose description is as follows:
Type: Integer
Purpose: Allow operating system to avoid duplicating post power-on delay on Sx resume flow
Description:
0: No (There is no hardware or firmware sequencing to provide post power-on reset delay to PCI
subsystem. This situation is the same as the legacy situation where this _DSM is not provided.)
1: Yes (System hardware or firmware assumes responsibility to provide post power-on reset delay to
the PCI subsystem. Operating System may assume all devices in the PCI subsystems have
completed power-on reset.)
4.6.9. _DSM for Specifying Device Readiness Durations
This section describes how system firmware can indicate to an operating system that it can lower the
PCI device initialization delays to less than the duration specified in the PCI Express Base Specification.
This provides an ACPI interface to provide information equivalent to the Readiness Time Reporting
extended capability structure. There are several delays covered in this _DSM:
1. For devices that support faster self-initialization after Conventional Reset (section 6.6.1 in PCI
Express Base Specification Rev 3.0).
2. For device that support faster recovery time following D3hot-to-D0 transition (section 5.3.1
Device Power Management States in PCI Express Base Specification).
3. For a function that has a shorter Functional Level Reset (FLR) latency (section 6.6.2
Function-Level Reset in PCI Express Base Specification).
4. For a device that has a shorter Data Link Up (DL_Up) latency (section 6.6.1 in PCI Express
Base Specification).
5. For a device (PF) supporting one or more VFs with a shorter VF enable latency (section
3.3.3.1 in PCI Express Base Specification).
This function is optional. If the platform does not provide it, the operating system must adhere to
all timing requirements as described in the PCI Express Base Specification and/or applicable form
factor specification, including values contained in a Readiness Time Reporting capability structure.
Operating systems that take advantage of this function can reduce PCI device initialization delay.
Values provided in this function can only be used to lower (reduce) the latency required by
specification or values discovered from device.
Delay values reported via this Function which are greater than the minimum delays required by the
PCI Express Base Specification should be ignored by operating system software.
Delay values reported by firmware must be interpreted as overriding any Configuration Ready
indicator from hardware, whether increasing or decreasing required delays. This includes ignoring
FRS and DRS notifications where overridden by this _DSM function, as well as ignoring values
specified in the Readiness Time Reporting extended capability structure, if present.
