---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 80
headings: []
---

# Source page 80

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  80
Return:
Integer
0h - Denied. Indicates that the platform cannot support the power requested. Software may retry
the request with either a lower power request or require no power removal. This is also the value
returned to signify any error with the request.
1h - Granted. Indicates that the device is permitted to draw the requested auxiliary power.
2h - No main power removal. Indicates that the platform will not remove main power from the
slot while the system is in S0. This value may be returned even though it was not requested that
main power remain on, based on requirements of other devices within the platform or other
platform configuration variations. This is the only valid return value when Arg3 is 8000 0000h.
11h to 1Fh - Retry, with interval. Indicates that the platform cannot support the power requested
at this time, but that it may be able to in the future. Software should retry the request in the
number of seconds corresponding with the lower 4 bits of the return value (1 to 15). Firmware is
not permitted to return a value in this range more than once for each _DSM instance (located
within the ACPI namespace of a single downstream port DeviceObject), unless there is a
subsequent invocation of this function before the previously returned retry interval has expired.
All other values are Reserved.

 IMPLEMENTATION NOTE
Platform Firmware Budgeting of Aux Power Availability
Platform firmware must not grant more power than what is available within the system. For
example, a board may be designed with four CEM slots (one x16 slot, one x4 slot, and two x1
slots). The board may implement a power delivery circuit capable of supplying 2 W of pow er for
the 3.3 Vaux rail supplying all 4 slots. The 3.3 Vaux pins on each CEM slot can supply 1 W each.
Platform firmware may use the retry mechanism to prioritize requests from devices i n preferred
slots in the following manner:
● Requests from a device in the highest priority slot (e.g., x16) are granted immediately, if
available.
● Requests from devices in lower priority slots (e.g., x2, x1) are initially rejected, with a retry
interval inversely proportional to the slot priority. For instance, if the x2 slot is higher priority
than the x1 slots, so the retry interval for the x2 slot may be 4 seconds, and the x1 slots may be
8 and 10 seconds.
● As requests are granted, the granted values are subtracted from the available budget.
● Retried requests are granted based on the remaining power budget or denied if insufficient
power budget is available. Another retry is not permitted.
● When there is insufficient power budget for a request, firmware may choose to keep main
power on and return no power removal (2h).
