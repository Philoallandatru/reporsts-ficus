---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 73
headings: ["4.6.6. _DSM Definitions for Latency Tolerance Reporting", "4.6.7. _DSM for Naming a PCI or PCI Express Device Under Operating Systems"]
---

# Source page 73

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  73
bridge windows, or bridge secondary and subordinate bus numbers of this device even
though this restriction applies to the hierarchy below a bridge (unless another _DSM in that
hierarchy also implements Function 5), the operating system is free to assign resources to
devices in this hierarchy that have invalid BAR, window, or bus number settings. There may
be a reduced level of hot plug capability support in this hierarchy due to resource
constraints.)
1: No (The operating system need not preserve any PCI resource assignments made by
firmware at boot time and it may reconfigure/rebalance BARs, bridge windows and bus
numbers in the hierarchy.)
4.6.6. _DSM Definitions for Latency Tolerance Reporting
This section describes how PCI Express firmware describes Latency Tolerance Reporting
information to the operating system.
For Root Complexes that support Latency Tolerance Reporting, there is a set of maximum latency
values that could never be exceeded in normal operation.  Firmware must convey the maximum
values for each Downstream Port embedded within the platform.  The operating system is
responsible for calculating latencies along the path between each Downstream Port and any
Upstream Port (Switch Upstream Port or Endpoint) supporting LTR beneath the port, and
programming the sum into the Upstream Port’s Latency Tolerance Reporting Extended Capability
Structure.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 2
Arg2: Function Index: 6
Arg3: Empty Package
Return:
A Package of four integers corresponding with the LTR encoding defined in the PCI Express Base
Specification, as follows:
Integer 0: Maximum Snoop Latency Scale
Integer 1: Maximum Snoop Latency Value
Integer 2: Maximum No-Snoop Latency Scale
Integer 3: Maximum No-Snoop Latency Value
These values correspond directly to the LTR Extended Capability Structure fields described in the
PCI Express Base Specification.
4.6.7. _DSM for Naming a PCI or PCI Express Device Under
Operating Systems
This interface will return a package with the following information relative to the device or slot:
❑ First entry of the package is the instance number.
