---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 81
headings: ["4.6.11. _DSM for Adding PERST# Assertion Delay"]
---

# Source page 81

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  81
4.6.11. _DSM for Adding PERST# Assertion Delay
The Add PERST# Assertion Delay function is used to convey the requirement for a fixed delay in
timing between the time the PME_TO_Ack message is received at the PCI Express Downstream
Port that originated the PME_Turn_Off message, and the time the platform asserts PERST# to the
slot during the corresponding Endpoint’s or PCI Express Upstream Port’s transition to D3cold while
the system is in an ACPI operational state. This delay is not guaranteed to be applied during the
transition to a system sleeping state. Assertion of PERST# may be an indicator that power to the
device is about to be removed. There is no guaranteed delay between assertion of PERST# and
power removal. If any Function on the device is armed for wake, auxiliary power rails required to
supply wake logic will not be turned off.
Host platforms implementing this feature must ensure that the delay is observed by the device that
is being transitioned to D3cold. Once set, this delay is met on every applicable D3cold transition of the
device. This function may be invoked multiple times, allowing the delay value to be changed at any
time, so that the new value can be applied for the next applicable D3cold transition of the device.
Location:
Support for the Add PERST# Assertion Delay function is only applicable for a _DSM Control
Method within the scope of a PCI Express Downstream Port terminated by any sort of add-in
slot/connector.
For bus hierarchies where multiple Functions reside beneath the PCI Express Downstream Port
supporting this _DSM function, system software is responsible for tracking and aggregating requests
from child devices and requesting the maximum of the requested delay values.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 4
Arg2: Function Index: 0Bh
Arg3: Integer. The value, in microseconds, of the delay needed between the PME_TO_Ack
message receipt at the PCI Express Downstream Port that originated the
PME_Turn_Off message, and the subsequent assertion of PERST# on the
corresponding slot. This delay is injected during a transition to D3cold during the ACPI
operational state (S0). It does not apply during transitions from the ACPI operational
state to an ACPI sleeping state (S3/S4/S5). The maximum permitted requested delay is
10 ms.
Return:
Integer:  If the request succeeded, it returns the value specified in Arg3. If the request failed
(e.g., if the request in Arg3 is greater than 10ms), it returns the value specified in Arg3 in the
most recent successful request, or 0 if there was no such request.
