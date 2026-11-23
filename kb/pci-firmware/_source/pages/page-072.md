---
source: "PCI_Firmware_v3.3_20210120_NCB.pdf"
page: 72
headings: ["4.6.5. _DSM for Preserving PCI Boot Configurations"]
---

# Source page 72

PCI SERVICES IN ACPI
PCI FIRMWARE SPECIFICATION
REVISION 3.3
JANUARY 20, 2021  72
4.6.5. _DSM for Preserving PCI Boot Configurations
This section describes how system firmware can indicate to an operating system that it should
preserve assignments of PCI bus numbers, I/O ports, and memory address space done by firmware,
or whether it can reassign those resources. The indication is exposed through Function 5 of the
_DSM ACPI method.
This _DSM function is optional.
Location:
This _DSM function can be placed under any object representing:
● A PCI Express host bridge (PNP0A08)
● A PCI Express Root Port, Switch Port, or Endpoint
● A PCI Express Root Port Complex Integrated Endpoint
● A Conventional PCI host bridge (PNP0A03)
●  Conventional PCI/PCI-X bridge
● A Conventional PCI/PCI-X device
The function that applies to a device is either:
● A _DSM Function 5 implemented by an ACPI object that represents the device itself (if present),
or
● _DSM Function 5 in the nearest ACPI namespace scope that encloses the device.
If Function 5 applies to a bridge, it applies to the bridge itself (BARs, windows, and
secondary/subordinate bus numbers), as well as to the hierarchy produced by the bridge, unless it is
overridden by another Function 5 lower in the hierarchy.
Note: The resources consumed by a PCI host bridge, including those it makes available on the PCI
root bus below it, are described by the bridge's _CRS method.  If an operating system needs to
change the root bus resources, it must do so by evaluating the host bridge _PRS and _SRS methods.
A host bridge that does not supply _PRS/_SRS is not configurable by the operating system.
Arguments:
Arg0: UUID: E5C937D0-3553-4d7a-9117-EA4D19C3434D
Arg1: Revision ID: lowest valid Revision ID value: 2
Arg2: Function Index: 5
Arg3: Empty Package
Return:
An integer whose description is as follows:
Type: Integer
Purpose: Preserve PCI device configuration
Description:
0: Yes (The operating system must preserve PCI resource assignments made by firmware at
boot time. Except while sizing BARs, the operating system must not modify device BARs,
