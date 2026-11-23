---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 75
headings: []
---

# Source page 75

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  75

IMPLEMENTATION NOTE
When implementing support for this method, the following should be considered: System firmware
should include this method for all applicable PCI or PCI Express devices, both embedded and in
PCI or PCI Express slots.  System firmware should assign appropriate instance numbers to each
device to influence the device labeling under operating system accordingly for the given platform
design.  For an example system configuration that includes two networking devices,
Table 4-10 shows a) the location for each device (Bus#, Device#, Function#), b) description of
device, c) _DSM (function 7) for each device, and d) the resultant sample device label as assigned
by an operating system that takes advantage of this method.  In case of this sample configuration,
operating system would sort the different networking devices in the system using the instance
numbers provided via _DSM, and assign lower NIC-label (NIC1) to device which has lower
instance number, as shown in Table 4-10.



Table 4-10:  Example Usage of Device/Slot Enumeration Ordering Hints
PCI/PCI Express Device
Location
System Device _DSM Fn 7 Package Operating System
Device Label
Bus 2, Device 4, Function 0 Networking device in PCI
Express Slot 1
(3, “PCIe Slot 1”) NIC 2
Bus 4, Device 8, Function 0 Embedded networking
device
(2, “Embedded NIC1”)  NIC 1
